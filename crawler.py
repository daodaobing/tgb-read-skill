# -*- coding: utf-8 -*-
"""
淘股吧精华文章获取技能 - 爬虫模块
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from config import (
    TGB_BASE_URL, TGB_JINGHUA_URL, TGB_BLOG_URL_TEMPLATE,
    HEADERS, REQUEST_TIMEOUT, MAX_RETRIES, PAGES_PER_FETCH,
    DATE_FORMAT, DATETIME_FORMAT, BLOGGERS, CACHE_FILE, CACHE_EXPIRY_HOURS
)


class TgbCrawler:
    """淘股吧爬虫类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _make_request(self, url: str, retries: int = MAX_RETRIES) -> Optional[str]:
        """发送HTTP请求"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"请求失败 (状态码: {response.status_code}): {url}")
            except requests.exceptions.RequestException as e:
                print(f"请求异常 (尝试 {attempt + 1}/{retries}): {e}")
        return None

    def _parse_jinghua_article(self, article_div) -> Optional[Dict]:
        """解析精华文章列表中的单篇文章（使用div结构）"""
        try:
            article = {}

            # 解析标题和链接
            title_div = article_div.find('div', class_='middle-list-tittle')
            if not title_div:
                return None

            link = title_div.find('a')
            if link:
                href = link.get('href', '')
                # 处理链接格式：可能是 'a/xxx' 或 '/a/xxx'
                if href.startswith('/'):
                    href = href[1:]
                article['article_id'] = href.replace('a/', '')
                article['article_url'] = f"{TGB_BASE_URL}/{href}"
                article['title'] = link.get_text(strip=True)

            # 解析评论数和浏览量
            yuedu_div = article_div.find('div', class_='middle-list-yuedu')
            if yuedu_div:
                yuedu_text = yuedu_div.get_text(strip=True)
                match = re.match(r'([\d,]+)\s*/\s*([\d,]+)', yuedu_text)
                if match:
                    article['comments'] = int(match.group(1).replace(',', ''))
                    article['views'] = int(match.group(2).replace(',', ''))

            # 回帖日期
            reply_div = article_div.find('div', class_='middle-list-reply')
            if reply_div:
                article['reply_date'] = reply_div.get_text(strip=True)

            # 作者信息
            user_div = article_div.find('div', class_='middle-list-user')
            if user_div:
                author_link = user_div.find('a')
                if author_link:
                    author_href = author_link.get('href', '')
                    if author_href.startswith('/'):
                        author_href = author_href[1:]
                    article['author_id'] = author_href.replace('blog/', '')
                    article['author_name'] = author_link.get_text(strip=True)
                    article['author_url'] = f"{TGB_BASE_URL}/{author_href}"

            # 发帖日期
            post_div = article_div.find('div', class_='middle-list-post')
            if post_div:
                article['post_date'] = post_div.get_text(strip=True)

            # 提取标签
            article['is_jinghua'] = '[精]' in article.get('title', '')
            article['is_hongbao'] = '[红包]' in article.get('title', '')
            article['is_vote'] = '[投票]' in article.get('title', '')

            return article
        except Exception as e:
            print(f"解析文章行异常: {e}")
            return None

    def _parse_blog_article(self, article_div) -> Optional[Dict]:
        """解析博主文章列表中的单篇文章（使用div结构）"""
        try:
            article = {}

            # 查找链接
            link = article_div.find('a')
            if link:
                href = link.get('href', '')
                if href.startswith('/'):
                    href = href[1:]
                article['article_id'] = href.replace('a/', '')
                article['article_url'] = f"{TGB_BASE_URL}/{href}"
                article['title'] = link.get_text(strip=True)

            # 从div文本中解析浏览/回复和日期
            div_text = article_div.get_text()

            # 解析浏览/回复 (格式: 231/9)
            match = re.search(r'([\d,]+)/([\d,]+)', div_text)
            if match:
                article['views'] = int(match.group(1).replace(',', ''))
                article['comments'] = int(match.group(2).replace(',', ''))

            # 解析日期 (格式: 2026-03-28 或 03-28)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}-\d{2})', div_text)
            if date_match:
                article['post_date'] = date_match.group(1)
                # 如果是短日期格式，补全年份
                if len(article['post_date']) == 5:
                    article['post_date'] = f"{datetime.now().year}-{article['post_date']}"

            # 解析文章类型
            article['type'] = '原'  # 默认原创
            article['is_jinghua'] = False
            article['is_hongbao'] = False

            title_text = article.get('title', '')
            if '[精]' in title_text:
                article['type'] = '精'
                article['is_jinghua'] = True
            if '[红包]' in title_text:
                article['is_hongbao'] = True

            return article
        except Exception as e:
            print(f"解析博主文章行异常: {e}")
            return None

    def fetch_jinghua_articles(self, page: int = 1, sort_by_reply: bool = False) -> List[Dict]:
        """获取精华文章列表"""
        sort_param = "0" if sort_by_reply else "1"
        url = f"{TGB_JINGHUA_URL}{page}-{sort_param}"

        html = self._make_request(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        # 查找文章列表容器
        article_lists = soup.find_all('div', class_='Nbbs-tiezi-lists')
        for article_div in article_lists:
            article = self._parse_jinghua_article(article_div)
            if article:
                articles.append(article)

        return articles

    def fetch_blogger_articles(self, user_id: str) -> List[Dict]:
        """获取指定博主的文章列表"""
        url = TGB_BLOG_URL_TEMPLATE.format(user_id=user_id)

        html = self._make_request(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        # 查找所有文章条目
        article_tittles = soup.find_all('div', class_='article_tittle')
        for article_div in article_tittles:
            article = self._parse_blog_article(article_div)
            if article:
                article['user_id'] = user_id
                articles.append(article)

        return articles

    def get_total_pages(self, html: str) -> int:
        """从HTML中提取总页数"""
        match = re.search(r'共\s*(\d+)\s*页', html)
        if match:
            return int(match.group(1))
        return 1

    def fetch_recent_jinghua(self, days: int = 1) -> List[Dict]:
        """获取最近N天的新增精华文章"""
        articles = []
        fetched_pages = 0
        max_pages = PAGES_PER_FETCH * 2  # 适当放宽限制

        cutoff_date = datetime.now() - timedelta(days=days)

        # 从第一页开始获取
        for page in range(1, max_pages + 1):
            page_articles = self.fetch_jinghua_articles(page)
            if not page_articles:
                break

            # 检查文章日期
            for article in page_articles:
                try:
                    # 解析发帖日期 (格式: MM-DD HH:MM)
                    post_date_str = article.get('post_date', '')
                    if len(post_date_str) == 11:  # MM-DD HH:MM
                        month, day_time = post_date_str.split('-')
                        day, time_part = day_time.split(' ')
                        hour, minute = time_part.split(':')
                        post_date = datetime(
                            datetime.now().year,
                            int(month),
                            int(day),
                            int(hour),
                            int(minute)
                        )

                        if post_date >= cutoff_date:
                            articles.append(article)
                        else:
                            # 已超出日期范围，停止获取
                            fetched_pages = page
                            break
                except Exception as e:
                    # 如果日期解析失败，保守地包含这篇文章
                    articles.append(article)

            if fetched_pages == page and fetched_pages > 0:
                break

            fetched_pages = page

        return articles

    def fetch_recent_blogger_articles(self, user_id: str, days: int = 1) -> List[Dict]:
        """获取指定博主最近N天的新增文章"""
        articles = self.fetch_blogger_articles(user_id)

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_articles = []

        for article in articles:
            try:
                post_date_str = article.get('post_date', '')
                # 尝试多种日期格式
                for fmt in ['%Y-%m-%d', '%m-%d', '%Y-%m-%d %H:%M']:
                    try:
                        if fmt == '%m-%d':
                            post_date = datetime.strptime(f"{datetime.now().year}-{post_date_str}", fmt)
                        else:
                            post_date = datetime.strptime(post_date_str, fmt)

                        if post_date >= cutoff_date:
                            recent_articles.append(article)
                        break
                    except:
                        continue
            except Exception:
                recent_articles.append(article)

        return recent_articles


class ArticleCache:
    """文章缓存管理"""

    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self.articles = self._load_cache()

    def _load_cache(self) -> Dict:
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载缓存失败: {e}")
        return {"jinghua": [], "bloggers": {}, "last_update": None}

    def _save_cache(self):
        """保存缓存"""
        try:
            os.makedirs(os.path.dirname(self.cache_file) if os.path.dirname(self.cache_file) else '.', exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.articles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def update_jinghua(self, articles: List[Dict]):
        """更新精华文章缓存"""
        self.articles["jinghua"] = articles
        self.articles["last_update"] = datetime.now().isoformat()
        self._save_cache()

    def update_blogger(self, user_id: str, articles: List[Dict]):
        """更新博主文章缓存"""
        self.articles["bloggers"][user_id] = articles
        self.articles["last_update"] = datetime.now().isoformat()
        self._save_cache()

    def get_new_articles(self, source: str, user_id: str = None) -> List[Dict]:
        """获取新增文章（与上次获取相比）"""
        if source == "jinghua":
            old_articles = self.articles.get("jinghua", [])
            old_ids = {a.get('article_id') for a in old_articles}

            crawler = TgbCrawler()
            new_articles = crawler.fetch_recent_jinghua(days=1)

            # 只返回新增文章
            return [a for a in new_articles if a.get('article_id') not in old_ids]

        elif source == "blogger" and user_id:
            old_articles = self.articles.get("bloggers", {}).get(user_id, [])
            old_ids = {a.get('article_id') for a in old_articles}

            crawler = TgbCrawler()
            new_articles = crawler.fetch_recent_blogger_articles(user_id, days=1)

            return [a for a in new_articles if a.get('article_id') not in old_ids]

        return []


def format_article_output(article: Dict, source: str = "jinghua") -> str:
    """格式化文章输出"""
    lines = []

    # 标题
    lines.append(f"📌 {article.get('title', '无标题')}")

    # 标签
    tags = []
    if article.get('is_jinghua'):
        tags.append("✨精华")
    if article.get('is_hongbao'):
        tags.append("🧧红包")
    if article.get('is_vote'):
        tags.append("🗳️投票")
    if tags:
        lines.append(f"   标签: {' | '.join(tags)}")

    # 链接
    lines.append(f"   链接: {article.get('article_url', '#')}")

    # 其他信息
    if source == "jinghua":
        lines.append(f"   作者: {article.get('author_name', '未知')} (ID: {article.get('author_id', 'N/A')})")
        lines.append(f"   评论/浏览: {article.get('comments', 0):,} / {article.get('views', 0):,}")
        lines.append(f"   发帖: {article.get('post_date', 'N/A')} | 回帖: {article.get('reply_date', 'N/A')}")
    elif source == "blogger":
        lines.append(f"   类型: {article.get('type', '原')}")
        lines.append(f"   阅读: {article.get('views', 0):,} | 评论: {article.get('comments', 0):,}")
        lines.append(f"   发布时间: {article.get('post_date', 'N/A')}")

    return '\n'.join(lines)


def get_enabled_bloggers() -> List[Dict]:
    """获取已启用的博主列表"""
    return [b for b in BLOGGERS if b.get('enabled', True)]
