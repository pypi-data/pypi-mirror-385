import trimesh
import pyrender
import numpy as np
from PIL import Image
from pathlib import Path
import sys
import click

def glb2png(glb_input, png_output=None, width=512, height=512):
    glb_input = Path(glb_input)
    if not glb_input.exists():
        raise FileNotFoundError(f"GLB not found: {glb_input}")

    if png_output is None:
        png_output = glb_input.with_suffix(".png")
    else:
        png_output = Path(png_output)

    scene_or_mesh = trimesh.load(glb_input, force='scene', skip_materials=True)

    meshes = []
    if isinstance(scene_or_mesh, trimesh.Scene):
        for geom in scene_or_mesh.geometry.values():
            if isinstance(geom, trimesh.Trimesh) and not geom.is_empty:
                meshes.append(geom)
    elif isinstance(scene_or_mesh, trimesh.Trimesh) and not scene_or_mesh.is_empty:
        meshes.append(scene_or_mesh)

    if len(meshes) == 0:
        raise ValueError(f"No usable meshes found in {glb_input}")

    mesh = trimesh.util.concatenate(meshes)
    mesh.apply_translation(-mesh.centroid)
    scale = 1.0 / max(mesh.extents)
    mesh.apply_scale(scale)

    material = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=[0.8, 0.8, 0.8, 1.0],
        metallicFactor=0.0,
        roughnessFactor=1.0,
    )
    render_mesh = pyrender.Mesh.from_trimesh(mesh, material=material, smooth=True)
    scene = pyrender.Scene(bg_color=[0, 0, 0, 0], ambient_light=[0.5, 0.5, 0.5])
    scene.add(render_mesh)

    light = pyrender.DirectionalLight(color=np.ones(3), intensity=2)
    scene.add(light, pose=np.eye(4))

    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
    camera_pose = np.eye(4)
    camera_pose[2, 3] = 1.5
    camera_pose[1, 3] = 0.1
    scene.add(camera, pose=camera_pose)

    r = pyrender.OffscreenRenderer(width, height)
    color, _ = r.render(scene)
    r.delete()

    Image.fromarray(color).save(png_output)
    print(f"Saved PNG: {png_output}")


def glbf2png(folder_input, width=512, height=512):
    folder_input = Path(folder_input)
    if not folder_input.exists():
        raise FileNotFoundError(f"Folder not found: {folder_input}")

    glb_files = list(folder_input.rglob("*.glb"))
    if len(glb_files) == 0:
        print(f"No GLB files found in {folder_input}")
        return

    for glb_file in glb_files:
        try:
            glb2png(glb_file, None, width, height)
        except Exception as e:
            print(f"Error with {glb_file}: {e}")


@click.group()
def cli():
    pass

@cli.command()
@click.argument("glb_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None)
def glb2png_cmd(glb_file, output):
    glb2png(glb_file, output)

@cli.command()
@click.argument("folder", type=click.Path(exists=True))
def glbf2png_cmd(folder):
    glbf2png(folder)


if __name__ == "__main__":
    cli()
