import asyncio
import base64
import datetime
import math
from pathlib import Path
from typing import Literal, Optional

import httpx
import orjson as json
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import Page, ElementHandle, FloatRect

from .browser import Browser
from .exceptions import ElementNotFound, RequiredURL
from .options import LegacyScreenshotOptions, PageScreenshotOptions, ElementScreenshotOptions, SectionScreenshotOptions, \
    SourceOptions
from ..constants import templates_path, elements_to_disable, max_screenshot_height, base_width, base_height

env = Environment(loader=FileSystemLoader(templates_path),
                  autoescape=True, enable_async=True)


def webrender_fallback(func):
    async def wrapper(self, options):
        if not self.browser.browser and not self.remote_only:
            self.logger.warning("WebRender browser is not initialized.")
            return None
        request_remote = False
        if self.remote_webrender_url and self.remote_only:
            self.logger.warning(
                "Local WebRender is disabled, using remote WebRender only.")
            request_remote = True
        else:
            try:
                self.logger.info(func.__name__ +
                                 " function called with options: " + str(options))
                return await func(self, options)
            except Exception:
                self.logger.exception(
                    f"WebRender processing failed with options: {options}:")
                if self.remote_webrender_url:
                    request_remote = True
        if request_remote:
            try:
                if self.remote_webrender_url:
                    self.logger.info(
                        "Trying get content from remote web render...")
                    remote_url = self.remote_webrender_url + func.__name__ + "/"
                    data = options.model_dump_json(exclude_none=True)
                    self.logger.info(
                        f"Remote URL: {remote_url}, Options: {data}")
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            remote_url,
                            data=data,
                            timeout=30,
                            follow_redirects=True
                        )
                        if resp.status_code != 200:
                            self.logger.error(f"Failed to render: {
                                resp.text}, status code: {resp.status_code}")
                            return None
                        return json.loads(resp.read())
            except Exception:
                self.logger.exception("Remote WebRender processing failed: ")
        return None

    return wrapper


class WebRender:
    browser: Browser = None
    debug: bool = False
    remote_webrender_url = None
    remote_only = False
    export_logs = False
    logs_path = None
    name = "AkariBot WebRender™"

    def __init__(self,
                 debug: bool = False,
                 remote_webrender_url: Optional[str] = None,
                 remote_only: bool = False,
                 export_logs = False,
                 logs_path = None,
                 name: str = None):
        """
        :param debug: If True, the browser will run on non-headless mode, the page will not be closed after the screenshot is taken.
        """
        self.debug = debug
        self.remote_webrender_url = remote_webrender_url
        if self.remote_webrender_url and self.remote_webrender_url[-1] != "/":
            self.remote_webrender_url += "/"
        self.remote_only = remote_only
        self.export_logs = export_logs
        if export_logs: 
            if logs_path:
                self.logs_path = Path(logs_path)
            else:
                self.logs_path = (Path(__file__).parent.parent.parent / "logs").resolve()
        if name:
            self.name = name

        if not self.browser:
            self.browser = Browser(debug=debug, logs_path=self.logs_path)
            self.browser_init = self.browser.browser_init
            self.browser_close = self.browser.close
            self.logger = self.browser.logger

    class RenderPage:

        def __init__(self, parent: 'WebRender', width=base_width, height=base_height, locale="zh_cn", content=None,
                     url=None, css=None, stealth=True):
            self.width = width
            self.height = height
            self.locale = locale
            self.content = content
            self.url = url
            self.css = css
            self.stealth = stealth
            self.browser = parent.browser
            self.debug = parent.debug

        async def __aenter__(self):
            self.start_time = datetime.datetime.now().timestamp()
            self.page = await self.browser.new_page(width=self.width,
                                                    height=self.height,
                                                    locale=self.locale,
                                                    stealth=self.stealth)
            if self.content:
                await self.page.set_content(self.content, wait_until="networkidle")
            if self.url:
                await self.page.goto(self.url, wait_until="networkidle")
            if self.content or self.url:
                with open(f"{templates_path}/custom.css", "r", encoding="utf-8") as f:
                    custom_css = f.read()
                await self.page.add_style_tag(content=custom_css)
                if self.css:
                    await self.page.add_style_tag(content=self.css)
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if not self.debug:
                await self.page.close()

    @staticmethod
    async def select_element(el: str | list, pg: Page) -> (ElementHandle, str):
        if isinstance(el, str):
            return (await pg.query_selector(el)), el
        for obj in el:
            rtn = await pg.query_selector(obj)
            if rtn is not None:
                return rtn, obj
        return None, None

    async def make_screenshot(self, page: Page, el: ElementHandle, screenshot_height: int = max_screenshot_height,
                              output_type: Literal["png", "jpeg"] = "jpeg", output_quality: int = 90) -> list[str]:
        await page.evaluate("window.scroll(0, 0)")
        await page.route("**/*", lambda route: route.abort())
        content_size = await el.bounding_box()
        dpr = page.viewport_size.get("deviceScaleFactor", 1)
        screenshot_height = math.floor(screenshot_height / dpr)
        self.logger.info(f"Content size: {content_size}, DPR: {
            dpr}, Screenshot height: {screenshot_height}")

        # If content height is less than max screenshot height, take a single screenshot and return as a list with one item

        if content_size.get("height") < max_screenshot_height:
            self.logger.info(
                "Content height is less than max screenshot height, taking single screenshot.")
            img = await el.screenshot(type=output_type,
                                      quality=output_quality if output_type == "jpeg" else None)
            return [base64.b64encode(img).decode()]

        # Otherwise, take multiple screenshots and return as a list with multiple items

        y_pos = content_size.get("y")
        total_content_height = content_size.get("y")
        images = []
        while True:
            if y_pos > content_size.get("height") + content_size.get("y"):
                break
            total_content_height += max_screenshot_height
            content_height = max_screenshot_height
            if total_content_height > content_size.get("height") + content_size.get("y"):
                content_height = content_size.get(
                    "height") + content_size.get("y") - total_content_height + max_screenshot_height
            await page.evaluate(f"window.scroll({content_size.get("x")}, {y_pos})")
            await asyncio.sleep(3)
            self.logger.info("X:" + str(content_size.get("x")) + " Y:" + str(y_pos) +
                             " Width:" + str(content_size.get("width")) + " Height:" + str(content_height))

            img = await page.screenshot(type=output_type,
                                        quality=output_quality if output_type == "jpeg" else None,
                                        clip=FloatRect(x=content_size.get("x"),
                                                       y=y_pos,
                                                       width=content_size.get(
                                                           "width"),
                                                       height=content_height), full_page=True)
            images.append(base64.b64encode(img).decode())
            y_pos += screenshot_height
        return images

    @classmethod
    async def add_count_box(cls, page: Page, element: str, start_time: float = datetime.datetime.now().timestamp()):
        with open(f"{templates_path}/add_count_box.js") as f:
            js_code = f.read()
        return await page.evaluate(js_code, {"selected_element": element, "start_time": int(start_time * 1000),
                                             "name": cls.name})

    async def select_element_and_screenshot(self,
                                            elements: str | list,
                                            page: Page,
                                            start_time: float,
                                            count_time=True,
                                            output_type: Literal["png", "jpeg"] = "jpeg",
                                            output_quality: int = 90):
        el, selected_ = await self.select_element(elements, page)
        if not el:
            raise ElementNotFound
        if count_time:
            await self.add_count_box(page, selected_, start_time)
        images = await self.make_screenshot(page, el, output_type=output_type,
                                            output_quality=output_quality)
        return images

    @webrender_fallback
    async def legacy_screenshot(self, options: LegacyScreenshotOptions):
        async with self.RenderPage(self,
                                   width=options.width,
                                   height=options.height,
                                   locale=options.locale,
                                   content=await env.get_template("content.html").render_async(language="zh-CN",
                                                                                               contents=options.content),
                                   url=options.url,
                                   css=options.css,
                                   stealth=options.stealth) as p:
            images = await self.select_element_and_screenshot(
                elements=["body > .mw-parser-output > *:not(script):not(style):not(link):not(meta)" if options.mw
                          else "body > *:not(script):not(style):not(link):not(meta)"],
                page=p.page,
                start_time=p.start_time,
                count_time=options.counttime,
                output_type=options.output_type,
                output_quality=options.output_quality
            )
            return images

    @webrender_fallback
    async def page_screenshot(self, options: PageScreenshotOptions):

        async with self.RenderPage(self,
                                   width=options.width,
                                   height=options.height,
                                   locale=options.locale,
                                   content=options.content,
                                   url=options.url,
                                   css=options.css,
                                   stealth=options.stealth) as p:
            images = await self.select_element_and_screenshot(
                elements=["body"],
                page=p.page,
                start_time=p.start_time,
                count_time=options.counttime,
                output_type=options.output_type,
                output_quality=options.output_quality
            )
            return images

    @webrender_fallback
    async def element_screenshot(self, options: ElementScreenshotOptions):
        async with self.RenderPage(self,
                                   width=options.width,
                                   height=options.height,
                                   locale=options.locale,
                                   content=options.content,
                                   url=options.url,
                                   css=options.css,
                                   stealth=options.stealth) as p:
            with open(f"{templates_path}/element_screenshot_evaluate.js", "r", encoding="utf-8") as f:
                js_code = f.read()

            await p.page.evaluate(js_code, elements_to_disable)
            images = await self.select_element_and_screenshot(
                elements=options.element,
                page=p.page,
                start_time=p.start_time,
                count_time=options.counttime,
                output_type=options.output_type,
                output_quality=options.output_quality
            )
            return images

    @webrender_fallback
    async def section_screenshot(self, options: SectionScreenshotOptions):
        async with self.RenderPage(self,
                                   width=options.width,
                                   height=options.height,
                                   locale=options.locale,
                                   content=options.content,
                                   url=options.url,
                                   css=options.css,
                                   stealth=options.stealth) as p:
            with open(f"{templates_path}/section_screenshot_evaluate.js", "r", encoding="utf-8") as f:
                js_code = f.read()

            await p.page.evaluate(js_code, {"section": options.section, "elements_to_disable": elements_to_disable})
            images = await self.select_element_and_screenshot(
                elements=".bot-sectionbox",
                page=p.page,
                start_time=p.start_time,
                count_time=options.counttime,
                output_type=options.output_type,
                output_quality=options.output_quality
            )
            return images

    @webrender_fallback
    async def source(self, options: SourceOptions):
        url = options.url
        if not url:
            raise RequiredURL
        async with self.RenderPage(self,
                                   locale=options.locale,
                                   url=options.url,
                                   stealth=options.stealth) as p:

            resp = await p.page.goto(url, wait_until="networkidle")
            if resp.status != 200:  # attempt to fetch the url content using fetch
                get = await p.page.request.fetch(url)
                if get.status == 200:
                    return get.text()
                self.logger.error(f"Failed to fetch URL: {
                    url}, status code: {get.status}")
                return None

            _source = await p.page.content()
            if options.raw_text:
                _source = await p.page.query_selector("pre")
                return await _source.inner_text()

            return _source
