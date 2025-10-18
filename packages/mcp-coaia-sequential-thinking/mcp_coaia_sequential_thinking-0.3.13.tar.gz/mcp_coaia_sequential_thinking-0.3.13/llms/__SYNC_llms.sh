mkdir -p ../__llms
tar cf - *md *txt | (cd ../__llms/ && tar xvf - && git add . && git commit . -m "sync:llms";git push)
