from json import dump
from typing import TYPE_CHECKING, override

from tumblrbot.utils.common import FlowClass, PreviewLive
from tumblrbot.utils.models import Post

if TYPE_CHECKING:
    from io import TextIOBase


class PostDownloader(FlowClass):
    @override
    def main(self) -> None:
        self.config.data_directory.mkdir(parents=True, exist_ok=True)

        with PreviewLive() as live:
            for blog_identifier in self.config.download_blog_identifiers:
                data_path = self.get_data_path(blog_identifier)

                completed = 0
                after = 0
                if data_path.exists():
                    lines = data_path.read_bytes().splitlines() if data_path.exists() else []
                    completed = len(lines)
                    if lines:
                        after = Post.model_validate_json(lines[-1]).timestamp

                with data_path.open("a", encoding="utf_8") as fp:
                    self.paginate_posts(
                        blog_identifier,
                        completed,
                        after,
                        fp,
                        live,
                    )

    def paginate_posts(self, blog_identifier: str, completed: int, after: int, fp: TextIOBase, live: PreviewLive) -> None:
        task_id = live.progress.add_task(f"Downloading posts from '{blog_identifier}'...", total=None, completed=completed)

        while True:
            response = self.tumblr.retrieve_published_posts(blog_identifier, after=after)
            live.progress.update(task_id, total=response.response.blog.posts, completed=completed)

            if not response.response.posts:
                return

            for post in response.response.posts:
                dump(post, fp)
                fp.write("\n")

                model = Post.model_validate(post)
                after = model.timestamp
                live.custom_update(model)

            completed += len(response.response.posts)
