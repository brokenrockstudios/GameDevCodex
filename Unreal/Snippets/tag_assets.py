import unreal
import sys
import argparse
from datetime import datetime

def run(search, creator, source=None, license="Fab", date=None, dry=False):
    if not hasattr(unreal, 'InterchangeBaseNodeContainer'):
        unreal.log_error("InterchangeBaseNodeContainer not available in this UE version - cannot safely clear node container. Aborting.")
        return

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    if source is None:
        source = search

    unreal.log(f"Search:    {search}")
    unreal.log(f"Source:    {source}")
    unreal.log(f"Creator:   {creator}")
    unreal.log(f"License:   {license}")
    unreal.log(f"Date:      {date}")
    unreal.log(f"Dry Run:   {dry}")

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    results = registry.get_assets_by_path(search, recursive=True)
    unreal.log(f"Found {len(results)} assets")

    cleared = 0
    tagged = 0

    for r in results:
        asset = unreal.load_asset(str(r.package_name))
        if asset is None:
            continue

        # Strip interchange data
        try:
            aid = asset.get_editor_property('asset_import_data')
            if aid is not None and "Interchange" in aid.get_class().get_name():
                if not dry:
                    aid.modify()
                    aid.set_pipelines([])
                    empty_container = unreal.new_object(unreal.InterchangeBaseNodeContainer, outer=aid)
                    aid.set_node_container(empty_container)
                cleared += 1
                unreal.log(f"{'[DRY] ' if dry else ''}Cleared interchange: {r.package_name}")
        except:
            pass

        # Tag metadata
        try:
            if not dry:
                unreal.EditorAssetLibrary.set_metadata_tag(asset, "Creator",      creator)
                unreal.EditorAssetLibrary.set_metadata_tag(asset, "SourceFolder", source)
                unreal.EditorAssetLibrary.set_metadata_tag(asset, "License",      license)
                unreal.EditorAssetLibrary.set_metadata_tag(asset, "ImportDate",   date)
            tagged += 1
        except:
            unreal.log_warning(f"Could not tag: {r.package_name}")

    unreal.log(f"Done - {'[DRY RUN] ' if dry else ''}cleared {cleared}, tagged {tagged}")

# main()
# def main():
#     if not hasattr(unreal, 'InterchangeBaseNodeContainer'):
#         unreal.log_error("InterchangeBaseNodeContainer not available in this UE version - cannot safely clear node container. Aborting.")
#         return
#     
#     # Strip the '--' separator UE adds before our args
#     args_raw = sys.argv[1:]
#     # if '--' in args_raw:
#     #    args_raw = args_raw[args_raw.index('--') + 1:]
#     normalized = []
#     for a in sys.argv[1:]:
#         normalized.append(a.lower() if a.startswith('-') else a)
# 
#     parser = argparse.ArgumentParser(prog="tag_assets")
#     parser.add_argument("-search",  required=True,          help="Path to search, e.g. /Game/RAW/ZenScape")
#     parser.add_argument("-source",  default=None,           help="Original import root (default: same as -search)")
#     parser.add_argument("-creator", required=True,          help="Creator name, e.g. \"Broken Rock Studios\"")
#     parser.add_argument("-license", default="Fab",          help="License (default: Fab)")
#     parser.add_argument("-date",    default=datetime.now().strftime("%Y-%m-%d"), help="Import date (default: today)")
#     parser.add_argument("-dry",     action="store_true",    help="Dry run, no saves")
# 
#     args = parser.parse_args(normalized)
#     
#     if args.source is None:
#         args.source = args.search
# 
#     unreal.log(f"Search:    {args.search}")
#     unreal.log(f"Source:    {args.source}")
#     unreal.log(f"Creator:   {args.creator}")
#     unreal.log(f"License:   {args.license}")
#     unreal.log(f"Date:      {args.date}")
#     unreal.log(f"Dry Run:   {args.dry}")
# 
#     registry = unreal.AssetRegistryHelpers.get_asset_registry()
#     results = registry.get_assets_by_path(args.search, recursive=True)
# 
#     unreal.log(f"Found {len(results)} assets")
#     cleared = 0
#     tagged = 0
