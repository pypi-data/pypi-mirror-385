import clearskies


class GitlabDefaultAuth(clearskies.di.AdditionalConfigAutoImport):
    def provide_gitlab_auth(self, environment: clearskies.Environment):
        secret_key = environment.get("GITLAB_AUTH_KEY", True)
        return clearskies.authentication.SecretBearer(secret_key=secret_key, header_prefix="Bearer ")
