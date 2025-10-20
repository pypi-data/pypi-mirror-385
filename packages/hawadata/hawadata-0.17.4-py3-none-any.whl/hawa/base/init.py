import inspect

from hawa.config import project


def build_set_project_params(p):
    """p 为 config.Settings"""
    f = inspect.signature(set_project)
    params = f.parameters
    func_params = {k: getattr(p, k.upper()) for k in params if k != 'self'}
    return func_params


def set_project(
        db_host: str = '',
        db_port: int = 3306,
        db_user: str = '',
        db_pswd: str = '',
        db_name: str = '',
        redis_host: str = '',
        redis_db: int = 0,
):
    for k, v in vars().items():
        upper_k = k.upper()
        if upper_k in dir(project):
            setattr(project, upper_k, v)
    project.COMPLETED = True
