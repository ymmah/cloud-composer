import jinja2

from definitions import TPL_PATH

template_loader = jinja2.FileSystemLoader(searchpath=TPL_PATH)
template_env = jinja2.Environment(loader=template_loader)
template_caches = {}


def render_template(template_name, *args, **kwargs):
    if template_name not in template_caches:
        template = template_env.get_template(template_name)
        template_caches[template_name] = template
    return template_caches[template_name].render(*args, **kwargs)
