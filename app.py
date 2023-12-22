from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_cors import CORS, cross_origin
import cloudinary, json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET_KEY"

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif","mp4", "mkv", "jfif"]
CORS(app)
cloudinary.config( 
  cloud_name = "dqk8ah8sy", 
  api_key = "558845463371578", 
  api_secret = "rLdBpCQ0uU0RBVEaiw9E0ppcG2g",
  secure = True
)

import cloudinary.uploader
import cloudinary.api
config = cloudinary.config(secure=True)

@app.route("/")
@app.route("/home")
def home():
  gallery = cloudinary.api.resources()
  folders = cloudinary.api.subfolders("Graphics")
  results = cloudinary.api.resources(type = "upload", prefix = "Graphics/Test")
  return render_template("index.html", gallery=gallery, folders=folders['folders'], results=results['resources'])

@app.route("/media/<string:parent_folder>/<string:folder_name>")
def asset_folder(parent_folder, folder_name):
  images = cloudinary.api.resources(type="upload", prefix=f"{parent_folder}/{folder_name}", max_results=50)
  videos = cloudinary.api.resources(type="upload", prefix=f"{parent_folder}/{folder_name}", max_results=50, resource_type="video")
  raw_media = cloudinary.api.resources(type="upload", prefix=f"{parent_folder}/{folder_name}", max_results=50, resource_type="raw")

  return render_template("view.html", images=images['resources'], videos=videos['resources'], raw=raw_media['resources'], folder=folder_name)

@app.route("/create-folder", methods=["POST", "GET"])
def create_folder():
  if request.method == "POST":
    new_folder = request.form.get("folder-name")
    cloudinary.api.create_folder(f"Graphics/{new_folder}")
    flash(f"Folder {new_folder} created successfully", category="success")
    return redirect(url_for('home'))
  return render_template("create-folder.html")

@app.route("/delete-folder/<string:folder_name>")
def delete_folder(folder_name):
  results = (cloudinary.api.resources(type="upload", prefix=f"Graphics/{folder_name}") or cloudinary.api.resources(type="upload", prefix=f"Graphics/{folder_name}", resource_type="video"))
  if results['resources']:
    flash("Cannot delete folder with media", category="danger")
  else:
    cloudinary.api.delete_folder(f"Graphics/{folder_name}")
    flash(f"Folder {folder_name} deleted successfully", category="success")
  return redirect(url_for('home'))

@app.route("/upload-media/<string:folder_name>", methods=["POST", "GET"])
@cross_origin()
def upload_media(folder_name):
  if request.method == "POST":
    files_list = request.files.getlist("image")
    for file in files_list:
      if file.filename.split(".")[-1].lower() not in ALLOWED_EXTENSIONS:
        flash(f"Only media of type  {ALLOWED_EXTENSIONS} are allowed", category="danger")
        return redirect(url_for("asset_folder", parent_folder="Graphics",folder_name=folder_name))
      if file and file.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
        cloudinary.uploader.upload(file, folder=f"Graphics/{folder_name}", resource_type="auto", use_filename=True)
      else:
        flash("An error occurred while uploading the media", category="danger")
        return redirect(url_for("asset_folder", parent_folder="Graphics",folder_name=folder_name))
    flash(f"Successfully uploaded media to folder '{folder_name}'", category="success")
    return redirect(url_for("asset_folder", parent_folder="Graphics",folder_name=folder_name))
  return render_template("upload-media.html", folder=folder_name)

@app.route("/delete-media/<string:parent_folder>/<string:folder_name>")
def delete_media(parent_folder, folder_name):
  (cloudinary.api.delete_resources_by_prefix(prefix=f"{parent_folder}/{folder_name}") and cloudinary.api.delete_all_resources(prefix=f"{parent_folder}/{folder_name}", resource_type="video"))
  flash(f"Media deleted successfully", category="success")
  return redirect(url_for('home'))

if __name__ == "__main__":
  app.run(debug=True)
