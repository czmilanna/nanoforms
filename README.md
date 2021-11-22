# Nanoforms

## Minimal Requirements

### Minimal Software Requirements
* Linux, recommended [Ubuntu 20.04 LTS](https://ubuntu.com/download/server)
* [Docker](https://www.docker.com/get-started)
* [docker-compose](https://docs.docker.com/compose/install/)
* [Make](https://www.gnu.org/software/make/)

### Minimal Hardware Requirements
* Processor: 	8 core 64bit
* Memory:		64GB RAM
* Disk Space:	1TB



## Deployment

### Step 1. Building images and deploying containers
Change `CHANGE_ME` secrets in `docker-compose.env` file and run below command:

```shell
sudo make deploy
```

### Step 2. Admin User creation
Run below command:
```shell
sudo make create_super_user
```

### Step 3. Accessing the Application
The application should be available at http://127.0.0.1:7337/




## Removal
Run below command:
```shell
sudo make destroy
```
