import logging
import requests
import planet_auth_utils


def main():
    logging.basicConfig(level=logging.DEBUG)
    auth_ctx = planet_auth_utils.PlanetAuthFactory.initialize_auth_client_context(auth_profile_opt="my-custom-profile")
    auth_ctx.ensure_request_authenticator_is_ready(allow_open_browser=True, allow_tty_prompt=True)
    result = requests.get(
        url="https://api.planet.com/basemaps/v1/mosaics",
        auth=auth_ctx.request_authenticator(),
        headers={"X-Planet-App": "requests-example"},
    )
    print(result.status_code)
    print(result.json())


if __name__ == "__main__":
    main()
