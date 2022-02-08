"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.login import log_in_page
from insta485.views.users import user_page
from insta485.views.followers import followers_page
from insta485.views.following import following_page
from insta485.views.posts import posts_page
from insta485.views.explore import explore_page
from insta485.views.account import (create_page,
                                    delete_page,
                                    edit_page,
                                    password_page)
