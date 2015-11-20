from django.http import HttpResponse


def XAccelRedirectResponse(file_path, file_name=None):
    """ This function create a http response with x-accel-redirect
     :param file_url protected url to the file
     :param file_name name of the file,
    """
    response = HttpResponse()
    response["Content-Disposition"] = "attachment; filename={0}".format(file_name)
    response["X-Accel-Redirect"] = file_path
    return response