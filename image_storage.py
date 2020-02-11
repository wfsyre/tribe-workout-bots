from google.cloud import storage
from firebase import firebase as fb
import encrypt
import os
import time
import ffmpeg
import requests
import slack_api
import resource


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
    image_blob.make_public()
    return image_blob.public_url


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
        f = open(file_name, 'wb')
        f.write(requests.get(img_urls[i][0]).content)
        f.close()
    slack_api.send_debug_message("Generating Movie", level="INFO")
    (
        ffmpeg.input('./*.jpg', pattern_type='glob', framerate=5).output(movie_name).run()
    )
    return movie_name


def slack_url_to_movie(img_urls):
    # resource.setrlimit(resource.RLIMIT_AS, (512, 1024))
    movie_name = 'movie.mp4'
    extensions = []
    send = True
    for i in range(len(img_urls)):
        extensions.append(".jpg")
        file_name = str(i) + extensions[i]
        f = open(file_name, 'wb')
        f.write(requests.get(img_urls[i],
                             headers={"Authorization": "Bearer " + os.getenv('OATH_ACCESS_TOKEN')}).content)
        f.close()
        # if send:
        #     slack_api.send_file(file_name, "#bot_testing")
        #     send = False
    slack_api.send_debug_message("Generating Movie", level="INFO")
    slack_api.send_debug_message(os.listdir('.'), level="INFO")
    (
        ffmpeg.input('*.jpg', pattern_type='glob', framerate=5)
        .output(movie_name)
        .run()
    )
    return movie_name
