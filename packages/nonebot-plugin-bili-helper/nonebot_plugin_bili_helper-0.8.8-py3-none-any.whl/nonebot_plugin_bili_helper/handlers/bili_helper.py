import asyncio
import json
import os
import re
import requests
import shutil
# import threading
from typing import Literal
from nonebot import get_driver, logger, on_message, on_regex
from nonebot_plugin_htmlrender import get_new_page
from nonebot.adapters.onebot.v11 import Event, Message, MessageSegment
from nonebot.matcher import Matcher
from aiohttp import web

from ..modules.bilibili_apis import BilibiliApis
from ..modules.bilibili_api_host import get_app
from ..modules.browser_adapter import BrowserMode
from ..config import config

driver = get_driver()

whitelist = config.analysis_whitelist
group_whitelist = config.analysis_group_whitelist
blacklist = config.analysis_blacklist
group_blacklist = config.analysis_group_blacklist
group_strategies = config.analysis_group_strategies

bili_helper_tmp_dir= config.bili_helper_tmp_dir

if os.path.exists(bili_helper_tmp_dir):
  shutil.rmtree(bili_helper_tmp_dir)
os.makedirs(bili_helper_tmp_dir, exist_ok=True)

cookie_store_path = config.bili_helper_cookie_path
def write_cookie(config: dict):
    try:
        with open(cookie_store_path, "w") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        logger.info('配置 {} 写入成功'.format(cookie_store_path))
        return True
    except Exception as e:
        logger.info('配置 {} 写入失败: {}'.format(cookie_store_path, e))
        return False
    
def read_cookie():
    config = { 'value': '' }
    try:
        with open(cookie_store_path, "r") as f:
            config = json.load(f)
        logger.info('配置 {} 读取成功'.format(cookie_store_path))
    except Exception as e:
        logger.info('配置 {} 为空或格式有误: {}\n准备创建默认配置'.format(cookie_store_path, e))
        write_cookie(config)
    return config

cookie_store = read_cookie()
# print('Loaded cookie:', cookie_store)

# 启动API服务
bili_helper_port = 9528
api_web = get_app(
    BrowserMode.NONEBOT_HTMLRENDER,
    cookie = cookie_store.get('value', ''),
)
api_web_runner = web.AppRunner(api_web.app)

@driver.on_startup
async def start_bili_helper_server():
    await api_web_runner.setup()
    site = web.TCPSite(api_web_runner, '127.0.0.1', bili_helper_port)
    await site.start()
    logger.info(f'BiliBili Helper API started at http://127.0.0.1:{bili_helper_port}')

@driver.on_shutdown
async def shutdown_bili_helper_server():
    await api_web_runner.cleanup()

bili_apis = BilibiliApis(
    cookie = cookie_store.get('value', ''),
)


async def is_allowed(event: Event) -> bool:
    user_id = str(event.get_user_id())
    group_id = str(
        event.group_id
        if hasattr(event, "group_id")
        else event.channel_id
        if hasattr(event, "channel_id")
        else None
    )

    if user_id in whitelist or group_id in group_whitelist:
        return True

    if len(whitelist) > 0 or len(group_whitelist) > 0:
        return False

    if user_id in blacklist or group_id in group_blacklist:
        return False

    return True

analysis_bili = on_message(
    rule=is_allowed,
    block=False,
    priority=8,
)

@analysis_bili.handle()
async def handle_analysis(event: Event, matcher: Matcher) -> None:

    async def fallback_bili_url(url: str, matcher: Matcher):
        await matcher.send(f"检测到B站链接: {url}")
        matcher.stop_propagation()

    group_id = str(
        event.group_id
        if hasattr(event, "group_id")
        else event.channel_id
        if hasattr(event, "channel_id")
        else None
    )

    message = event.get_message()
    bili_url = None
    mode: Literal["detail+comments", "link+comments", None] = None

    # 先在小程序段里找
    for seg in message:
        if (seg.type == "json"):
            json_str = str(seg.data.get("data", {}))
            data = json.loads(json_str)

            app = data.get("app", "")
            meta = data.get("meta", {})
            if re.match(r"^com\.tencent\.miniapp(_|\.|$)", app):
                detail = None
                for k, v in meta.items():
                    if k.startswith("detail_"):
                        detail = v
                        break
                if not detail:
                    return
                url = detail.get("qqdocurl", "")
                logger.info(f"解析到小程序链接: {url}")
                if not url or not re.match(r"^https?://b23\.tv", url):
                    return
                bili_url = url
                mode = "link+comments"
                break
            if re.match(r"^com\.tencent\.tuwen(\.|$)", app):
                news = meta.get("news", {})
                url = news.get("jumpUrl", "")
                logger.info(f"解析到图文链接: {url}")
                if not url or not re.match(r"^https?://b23\.tv", url):
                    return
                bili_url = url
                mode = "detail+comments"
                break

    # 如果没有在小程序里找到，就在纯文本里找
    if not bili_url:
        text = event.get_plaintext().strip()
        bili_url = bili_apis.get_url_from_text(text)
        if bili_url:
            mode = 'detail+comments'

    # 如果还是没有找到，就直接返回
    if not bili_url:
        return

    is_info_sent = False
    try:
        matcher.stop_propagation()
        strategy = group_strategies.get(group_id, None)
        def is_mode_allowed(m: str) -> bool:
            if not strategy:
                return True
            return m in strategy
        # url = quote(bili_url)
        vids = bili_apis.get_id_from_url(bili_url)
        if not vids:
            logger.warning(f"无法从链接中提取ID: {bili_url}")
            return
        logger.debug(f"提取到的ID: {vids}")
        info = bili_apis.video_info_api(bvid=vids.get("bv")).call().get("data", {})
        if is_mode_allowed("detail") and "detail" in mode:
            def number_readable(num: int) -> str:
                if num >= 1_0000_0000: return f"{num / 1_0000_0000:.1f}亿"
                elif num >= 1_0000: return f"{num / 1_0000:.1f}万"
                else: return str(num)

            def format_duration(seconds: int) -> str:
                if seconds < 60:
                    return f"00:{seconds:02d}"
                elif seconds < 3600:
                    minutes = seconds // 60
                    seconds = seconds % 60
                    return f"{minutes:02d}:{seconds:02d}"
                else:
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    seconds = seconds % 60
                    return f"{hours}:{minutes:02d}:{seconds:02d}"

            title = info.get("title", "未知标题")
            cover_url = info.get("pic", "")
            artist = info.get("owner", {}).get("name", "未知作者")
            type_name = info.get("tname", "未知分区")
            stat = info.get("stat", {})
            play_count = number_readable(stat.get("view", 0))
            # danmaku_count = number_readable(stat.get("danmaku", 0))
            like_count = number_readable(stat.get("like", 0))
            coin_count = number_readable(stat.get("coin", 0))
            # favorite_count = number_readable(stat.get("favorite", 0))
            duration = format_duration(info.get("duration", 0))
            desc = info.get("desc", "")

            msg_seg = [
                MessageSegment.text(f'{title}\n')
            ]

            try:
                if cover_url:
                    cover_img = requests.get(cover_url, timeout=10)
                    msg_seg.append(MessageSegment.image(cover_img.content))
            except Exception as e:
                logger.warning(f"获取封面失败: {e}")

            info_text = f"👤 {artist}\n" \
                        f"🔖 {type_name}  📼 {duration}\n" \
                        f"▶️ {play_count}  👍 {like_count}  🪙 {coin_count}"
            msg_seg.append(MessageSegment.text(info_text))

            if desc:
                if len(desc) > 300:
                    desc = desc[:300] + "..."
                desc_lines = desc.splitlines()
                if len(desc_lines) > 3:
                    desc = "\n".join(desc_lines[:3]).rstrip("...") + "..."
                msg_seg.append(MessageSegment.text(f"\nℹ️ {desc}"))
            await matcher.send(msg_seg)
            is_info_sent = True
        if is_mode_allowed("link") and "link" in mode:
            bvid = info.get("bvid", "")
            new_url = f"https://b23.tv/{bvid}" if bvid else bili_url
            await matcher.send(f"解析到B站链接: {new_url}")
            is_info_sent = True
        if is_mode_allowed("comments") and "comments" in mode:
            tmp_name = f"{int(event.time)}_{event.get_session_id()}"
            # comments_html = requests.get(f"{bili_helper_host}/get-replies?url={url}", timeout=20)
            url = f'http://127.0.0.1:{bili_helper_port}/render/comments?bvid={info.get("bvid","")}'
            # 使用线程池执行同步的 requests.get，避免阻塞事件循环
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, requests.get, url, 20)
            response.raise_for_status()
            result = json.loads(response.text)
            if result.get("code", -1) != 0:
                raise Exception(f"获取评论失败: {result.get('message', '未知错误')}")
            data = result.get("data", {})

            comments_html = data.get("html", "")
            comments_path = os.path.join(bili_helper_tmp_dir, f"{tmp_name}.html")
            with open(comments_path, "w", encoding="utf-8") as f:
                f.write(comments_html)
            logger.info(f"评论页已保存到 {comments_path}")
            async with get_new_page(
                device_scale_factor=1.0,
            ) as page:
                comments_full_path = os.path.abspath(comments_path)
                await page.goto("file://" + comments_full_path)
                await page.wait_for_load_state("networkidle")
                comments_img_path = os.path.join(bili_helper_tmp_dir, f"{tmp_name}.jpg")
                await page.screenshot(path=comments_img_path, full_page=True, type="jpeg", quality=80)
                logger.info(f"评论截图已保存到 {comments_img_path}")
                comments_img = open(comments_img_path, "rb").read()
                meg = Message(MessageSegment.image(comments_img))
                await matcher.send(meg)
                os.remove(comments_path)
                os.remove(comments_img_path)
    except Exception as e:
        logger.error(f"处理B站链接失败: {e}")
        if is_mode_allowed("link") and "link" in mode and not is_info_sent:
            await fallback_bili_url(bili_url, matcher)
    pass

set_cookie_pattern = rf"^设置B站Cookie\s*(.+)?$"
set_cookie_sniffer = on_regex(set_cookie_pattern, flags=re.DOTALL, priority=5, block=True)
@set_cookie_sniffer.handle()
async def handle_set_cookie(event: Event, matcher: Matcher) -> None:
    user_id = str(event.get_user_id())
    if not user_id in config.superusers:
        return
    text = event.get_plaintext().strip()
    m = re.match(set_cookie_pattern, text, flags=re.DOTALL)
    if not m:
        return
    cookie_value = m.group(1).strip() if m.group(1) else ""
    if not cookie_value:
        await matcher.send("请提供Cookie内容")
        return
    cookie_store['value'] = cookie_value
    write_cookie(cookie_store)
    bili_apis.set_cookie(cookie_value)
    api_web.set_cookie(cookie_value)
    await matcher.send("B站Cookie已更新")
