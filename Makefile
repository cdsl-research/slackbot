NAME=cdsl-slackbot
VER=v0.1

build:
	sudo docker build -t $(NAME) .

run:
	sudo docker run -it --rm -p 3100:3000 --name $(NAME) $(NAME)

exec:
	sudo docker exec -it $(NAME) sh

push:
	sudo docker tag $(NAME) us.gcr.io/third-ridge-246401/$(NAME):$(VER)
	sudo docker push us.gcr.io/third-ridge-246401/$(NAME):$(VER)
