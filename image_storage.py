from google.cloud import storage
from firebase import firebase as fb
import encrypt
import os
import time
import ffmpeg


def upload_image(path_to_image, poster_name, extension):
    ts = time.time()
    encrypt.decrypt('encrypted', os.environ['encryption_key'], 'credentials.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
    fb.FirebaseApplication('https://tribe-images.appspot.com')
    client = storage.Client()
    bucket = client.get_bucket('tribe-images.appspot.com')
    # posting to firebase storage
    image_blob = bucket.blob(poster_name + "/" + poster_name.lower() + str(ts) + extension)
    image_blob.upload_from_filename(path_to_image)
    return image_blob.public_url

#
def images_to_movie(img_urls):
    print(img_urls)
    encrypt.decrypt('encrypted', os.environ['encryption_key'], 'credentials.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
    fb.FirebaseApplication('https://tribe-images.appspot.com')
    client = storage.Client()
    movie_name = 'movie.mp4'
    extensions = []
    for i in range(len(img_urls)):
        extensions.append(img_urls[i][0][img_urls[i][0].rfind('.'):])
        file_name = str(i) + extensions[i]
        print("File name:", file_name)
        f = open(file_name, 'wb')
        client.download_blob_to_file(img_urls[i][0], f)
        f.close()
    (
        ffmpeg
            .input('*.jpg', pattern_type='glob', framerate=5)
            .output(movie_name)
            .run()
    )
    return movie_name
