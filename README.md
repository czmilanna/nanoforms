# Nanoforms

### Requirements
* linux
* docker
* docker-compose
* make

### Deploy
Change `docker-compose.env` file and run below command:
```shell
make deploy
```
App should be accessible on http://127.0.0.1:7337/

### Admin User creation
Run below command:
```shell
make create_super_user
```

### Destroy
Run below command:
```shell
make deploy
```