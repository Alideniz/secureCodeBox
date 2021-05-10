import os
import pytest
import requests
import logging
import pytest

from zapv2 import ZAPv2
from requests.exceptions import ConnectionError

from scbzapv2.zap_configuration import ZapConfiguration
from scbzapv2.zap_context import ZapConfigureContext
from scbzapv2.zap_spider import ZapConfigureSpider
from scbzapv2.zap_scanner import ZapConfigureActiveScanner
from scbzapv2.zap_extended import ZapExtended

def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "", "docker-compose.test.yaml")

@pytest.fixture(scope="session")
def get_bodgeit_url(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("bodgeit", 8080)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url

@pytest.fixture(scope="session")
def get_juiceshop_url(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("juiceshop", 3000)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url

@pytest.fixture(scope="session")
def get_zap_url(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("zap", 8090)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url

@pytest.fixture(scope="session")
def get_zap_instance(docker_ip, docker_services, get_zap_url) -> ZAPv2: 
    
    # MANDATORY. Define the API key generated by ZAP and used to verify actions.
    apiKey = 'eor898q1luuq8054e0e5r9s3jh'

    # MANDATORY. Define the listening address of ZAP instance
    localProxy = {
        "http": "http://127.0.0.1:8010",
        "https": "http://127.0.0.1:8010"
    }

    logging.info('Configuring ZAP Instance with %s', localProxy)
    # Connect ZAP API client to the listening address of ZAP instance
    zap = ZAPv2(proxies=localProxy, apikey=apiKey)

    return zap

@pytest.mark.integrationtest
def test_all_services_available(get_bodgeit_url, get_juiceshop_url, get_zap_url):
    response = requests.get(get_bodgeit_url + "/bodgeit/")
    assert response.status_code == 200
    
    response = requests.get(get_juiceshop_url + "/#/")
    assert response.status_code == 200

    response = requests.get(get_zap_url + "/UI/core/")
    assert response.status_code == 200

# @pytest.mark.integrationtest
# def test_scb_scan_without_config(get_zap_instance: ZAPv2):

#     zap = get_zap_instance
#     test_target = "http://www.secureCodeBox.io/"
    
#     zap_extended = ZapExtended(zap=zap, config_dir="")
#     zap_extended.scb_scan(target=test_target)
    
#     alerts = zap_extended.get_zap_scan().get_alerts(test_target, [], [])

#     logging.info('Found ZAP Alerts: %s', str(len(alerts)))

#     assert int(len(alerts)) >= 1

# @pytest.mark.integrationtest
# def test_bodgeit_scan_without_config(get_bodgeit_url, get_zap_instance: ZAPv2):

#     zap = get_zap_instance
#     test_target = "http://localhost:8080/bodgeit/"
    
#     zap_extended = ZapExtended(zap=zap, config_dir="")
#     zap_extended.scb_scan(target=test_target)
    
#     alerts = zap_extended.get_zap_scan().get_alerts(test_target, [], [])

#     logging.info('Found ZAP Alerts: %s', str(len(alerts)))

#     assert int(len(alerts)) >= 5

# @pytest.mark.integrationtest
# def test_bodgeit_scan_with_config(get_bodgeit_url, get_zap_instance: ZAPv2):

#     zap = get_zap_instance
#     test_config_yaml = "./tests/mocks/scan-full-bodgeit-local/"
#     test_target = "http://localhost:8080/bodgeit/"
    
#     zap_extended = ZapExtended(zap=zap, config_dir=test_config_yaml)
#     zap_extended.scb_scan(target=test_target)
    
#     alerts = zap_extended.get_zap_scan().get_alerts(test_target, [], [])

#     logging.info('Found ZAP Alerts: %s', str(len(alerts)))

#     assert int(len(alerts)) >= 5
    
# @pytest.mark.integrationtest
# def test_juiceshop_scan_without_config(get_juiceshop_url, get_zap_instance: ZAPv2):
    
#     zap = get_zap_instance
#     test_config_yaml = "./tests/mocks/scan-full-juiceshop-local/"
#     test_target = "http://localhost:3000/"
    
#     zap_extended = ZapExtended(zap=zap, config_dir="")
#     zap_extended.scb_scan(target=test_target)
    
#     alerts = zap_extended.get_zap_scan().get_alerts(test_target, [], [])

#     logging.info('Found ZAP Alerts: %s', str(len(alerts)))
    
#     assert int(len(alerts)) >= 2

@pytest.mark.integrationtest
def test_juiceshop_scan_with_config(get_juiceshop_url, get_zap_instance: ZAPv2):
    
    zap = get_zap_instance
    test_config_yaml = "./tests/mocks/scan-full-juiceshop-local/"
    test_target = "http://localhost:3000/"
    
    zap_extended = ZapExtended(zap=zap, config_dir=test_config_yaml)
    zap_extended.scb_scan(target=test_target)
    
    alerts = zap_extended.get_zap_scan().get_alerts(test_target, [], [])

    logging.info('Found ZAP Alerts: %s', str(len(alerts)))
    
    assert int(len(alerts)) >= 2
