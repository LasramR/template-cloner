from os import sep

from ..utils import fs, config, input
from ..utils.logger import ColorTable, ColorReset
from ..actions.template import preview_project
from ..options import OrcaOptions

def preview(options : OrcaOptions) -> bool:
  if options['command']['name'] != "preview":
    raise Exception("preview: invalid options")
  
  project_dir = options["command"]["project_dir"]
  orcarc_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{project_dir}{sep}.orcarc", ["", ".json", ".jsonc"]))

  if orcarc_file_path == None:
    options["logger"].warn(f"no orcarc(.json)? file has been found: no more work to do. exiting")
    return True

  orca_config = config.load_orca_config(orcarc_file_path)

  if orca_config == None:
    raise Exception(f"cloud not preview project becasuse of broken orca config (see {orcarc_file_path})")
  
  options["logger"].info(f"previewing project {project_dir}")
  variables = {}
  for v in orca_config.template.variables.keys():
    variables[orca_config.template.variables[v].name] = input.get_user_variable_input(orca_config.template.variables[v])

  project_preview = preview_project(project_dir, variables)

  options["logger"].success(f"project preview generated")

  if len(project_preview.directory_preview.keys()):
    options["logger"].info(f"directory change(s) ({len(project_preview.directory_preview.keys())})")
  for k in project_preview.directory_preview.keys():
    options["logger"].info(f"{k} -> {project_preview.directory_preview[k]}")

  if len(project_preview.file_preview.keys()):
    options["logger"].info(f"file change(s) ({len(project_preview.file_preview.keys())})")
  for k in project_preview.file_preview.keys():
    options["logger"].info(f"{k} -> {project_preview.file_preview[k]}")

  if len(project_preview.file_content_preview.keys()):
    options["logger"].info(f"content change(s) ({len(project_preview.file_content_preview.keys())})")

  for k in project_preview.file_content_preview.keys():
    for c in project_preview.file_content_preview[k]:
      options["logger"].info(f"{k} line {c.line}")
      print(f"{ColorTable["RED"]}- {c.raw}{ColorReset}")
      print(f"{ColorTable["GREEN"]}- {c.parsed}{ColorReset}")