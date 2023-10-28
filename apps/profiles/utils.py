import uuid


def profile_photo_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return "profiles/{0}".format(filename)


def verification_document_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return "verification_documents/{0}".format(filename)
