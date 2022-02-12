# task
- [ ] todo
- [ ] Delete all the jinja template code that displays the feed in insta485/templates/index.html
- [ ] GET	/api/v1/	Return API resource URLs
- [ ] GET	/api/v1/posts/	Return 10 newest post urls and ids
- [ ] GET	/api/v1/posts/?size=N	Return N newest post urls and ids
- [ ] GET	/api/v1/posts/?page=N	Return N’th page of post urls and ids
- [ ] GET	/api/v1/posts/?postid_lte=N	Return post urls and ids no newer than post id N
- [ ] GET	/api/v1/posts/<postid>/	Return one post, including comments and likes
- [ ] POST	/api/v1/likes/?postid=<postid>	Create a new like for the specified post id
- [ ] DELETE	/api/v1/likes/<likeid>/	Delete the like based on the like id
- [ ] POST	/api/v1/comments/?postid=<postid>	Create a new comment based on the text in the JSON body for the specified post id
- [ ] DELETE	/api/v1/comments/<commentid>/	Delete the comment based on the comment id
