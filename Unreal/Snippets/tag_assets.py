import unreal
import sys
import argparse
from datetime import datetime

# Script to clean up corrupted/bad interchange format
# Also allows a way to tag metadata to be attached to imported assets.

def main():
    if not hasattr(unreal, 'InterchangeBaseNodeContainer'):
        unreal.log_error("InterchangeBaseNodeContainer not available in this UE version - cannot safely clear node container. Aborting.")
        return
    
    # Strip the '--' separator UE adds before our args
    args_raw = sys.argv[1:]
    # if '--' in args_raw:
    #    args_raw = args_raw[args_raw.index('--') + 1:]
    normalized = []
    for a in sys.argv[1:]:
        normalized.append(a.lower() if a.startswith('-') else a)

    parser = argparse.ArgumentParser(prog="tag_assets")
    parser.add_argument("-search",  required=True,          help="Path to search, e.g. /Game/RAW/ZenScape")
    parser.add_argument("-source",  default=None,           help="Original import root (default: same as -search)")
    parser.add_argument("-publisher", required=True,        help="Publisher name, e.g. TonyTheng-Art")
    parser.add_argument("-license", default="Fab",          help="License (default: Fab)")
    parser.add_argument("-date",    default=datetime.now().strftime("%Y-%m-%d"), help="Import date (default: today)")
    parser.add_argument("-dry",     action="store_true",    help="Dry run, no saves")

    args = parser.parse_args(args_raw)
    
    if args.source is None:
        args.source = args.search

    unreal.log(f"Search:    {args.search}")
    unreal.log(f"Source:    {args.source}")
    unreal.log(f"Publisher: {args.publisher}")
    unreal.log(f"License:   {args.license}")
    unreal.log(f"Date:      {args.date}")
    unreal.log(f"Dry Run:   {args.dry}")

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    results = registry.get_assets_by_path(args.search, recursive=True)

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
                if not args.dry:
                    aid.modify()
                    aid.set_pipelines([])
                    empty_container = unreal.new_object(unreal.InterchangeBaseNodeContainer, outer=aid)
                    aid.set_node_container(empty_container)
                cleared += 1
                unreal.log(f"{'[DRY] ' if args.dry else ''}Cleared interchange: {r.package_name}")
        except:
            pass

        # Tag metadata
        try:
            if not args.dry:
                unreal.EditorAssetLibrary.set_metadata_tag(asset, "Publisher",   args.publisher)
                unreal.EditorAssetLibrary.set_metadata_tag(asset, "SourceFolder", args.source)
                unreal.EditorAssetLibrary.set_metadata_tag(asset, "License",     args.license)
                unreal.EditorAssetLibrary.set_metadata_tag(asset, "ImportDate",  args.date)
            tagged += 1
        except:
            unreal.log_warning(f"Could not tag: {r.package_name}")

    unreal.log(f"Done - {'[DRY RUN] ' if args.dry else ''}cleared {cleared}, tagged {tagged}")

main()
