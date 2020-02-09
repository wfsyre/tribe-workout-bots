from google.cloud import storage
from firebase import firebase as fb
import encrypt
import os
import time
import glob


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
    encrypt.decrypt('encrypted', os.environ['encryption_key'], 'credentials.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
    fb.FirebaseApplication('https://tribe-images.appspot.com')
    client = storage.Client()
    movie_name = 'movie.avi'
    extensions = []
    for i in range(len(img_urls)):
        extensions.append(img_urls[img_urls[i].rfind('.'):])
        client.download_blob_to_file(img_urls[0], open(str(i) + extensions[i]))
    img_array = []
    size = 0
    for i in range(len(img_urls)):
        img = cv2.imread(str(i) + extensions[i])
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)
    out = cv2.VideoWriter(movie_name, cv2.VideoWriter_fourcc(*'DIVX'), 15, size)

    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    return movie_name
