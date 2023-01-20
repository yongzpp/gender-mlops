from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer

from ingest_data import main_flow

docker_block = DockerContainer.load("gender-docker")

docker_dep = Deployment.build_from_flow(
    flow=main_flow,
    name="docker-flow",
    infrastructure=docker_block
)

if __name__=="__main__":
    docker_dep.apply()