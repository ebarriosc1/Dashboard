
import pandas as pd
from arusdUtils.creds import retrieve_credentials
from arusdUtils import check_file
from arusdUtils import directory
import logging
import pysftp
import paramiko
from base64 import decodebytes
import datetime
import socket
import os
import ssl
try:
    import truststore
    truststore.inject_into_ssl()
except ModuleNotFoundError:
    print("Truststore not installed - please add it if possible. Truststore should help with self-signed certificates issues.\
                If it's working without that's fine, but I recommend using it if you can.")
    pass

def retrieveData():
    log = logging.getLogger()

    def get_county_file(destination_filename="all_qss_users.tsv", source_filename='perpay.txt', directory=None, force=False):
        """
        Gets a list of users from the QSS SFTP system. Saves it to the local directory.


        :param force: force re-downloading even if the file exists in the local directory
        :param directory: directory to save the file under
        :param source_filename: filename to fetch
        :param destination_filename: filename of the output
        :return: the same filename (on success)
        """
        file_exists, destination_filename, directory = check_file(destination_filename, directory)
        if file_exists:
            if force is False:
                log.info(f"County {source_filename} already downloaded for today, {directory}")
                log.debug("Not downloading it again! Use the force option to override.")
                return destination_filename
            elif force is True:
                log.info(f"{source_filename} already downloaded, but downloading again anyway")

        county = "204.88.135.142"
        username, password = retrieve_credentials("Qss_Data_Warehouse")
        cnopts = pysftp.CnOpts()
        if cnopts.hostkeys.lookup(county) is None:
            log.warning(f"No host key configured for the County IP Address ({county}), adding a fail-back key")
            # noinspection SpellCheckingInspection
            key = paramiko.RSAKey(data=decodebytes(b"AAAAB3NzaC1yc2EAAAABEQAAAYEAyWk4IYoDw9P+y05eR9b8Rd0wDtDeo3BFwy0GijmvPYu2ZS"
                                                b"hCH/q0G5Einh1xxbomgfur+WWVbSYwJsUAhaPtgUKl/oZB85jWurxIJtOnpAs6w3MagQ6gcfMR"
                                                b"vaFvGXNPwQtEou8BW4EYAtUlEvwsQK7Jge8NI0lnpsGpVGWugR3s2xO470sf/dFKqaGznI3iuc"
                                                b"C3ATt1snFMfD+Jd1egdjp/sb4VqxWkAWPAc0rM2usIfr/zCeJsqTazrQx2/xzBseHEmqNEVJQa"
                                                b"FNz1ntt5varOQ8aaPTaicjhhqTfW1agIvPXSrJ1fzZSLPBJsWBd9HGSf44n+ZgJYlLE1k73VK2"
                                                b"8XHbVyJ0ea+aCLlw5Hy2hYKSfSWXPO2N+3DU9ADX3uloYvFTM/eTYsUVqaSTG6Qif6cx0h8THu"
                                                b"Q6L94rveIyeoawjT35kFOaFwSnhvz/A0nNr3u/zzsMO3FtzMdkJR0JCX4atmjas3WIVO4ifUf3"
                                                b"4UK0gd/Gx37tYVEL5bqkj1"))
            # inspection SpellCheckingInspection
            cnopts.hostkeys.add(county, "ssh-rsa", key)

        try:
            with pysftp.Connection(host=county,
                                username=username,
                                password=password,
                                cnopts=cnopts) as sftp:
                with sftp.cd("/"):
                    try:
                        sftp.get(source_filename, localpath=destination_filename, preserve_mtime=True)
                        log.info(f"Wrote file to {destination_filename}")

                        # Check how recently the files have been updated - if it's been longer than a day, warn somebody.
                        #   Something might be wrong with the QSS extract, or the SFTP failed or something.
                        mtime = datetime.datetime.date(datetime.datetime.fromtimestamp(os.path.getmtime(destination_filename)))
                        today = datetime.datetime.date(datetime.datetime.now())
                        dif = (today - mtime).days
                        if dif > 0:
                            log.info(f"File {destination_filename} was updated {dif} days ago!")
                        if dif >= 2:
                            log.warning(f"Files should be modified nightly, something may be up with the extract! {destination_filename}")

                    except paramiko.ssh_exception.SSHException as exc:
                        log.warning("Error connecting to server! Host key may have changed or be invalid.")
                        raise exc
        except paramiko.ssh_exception.SSHException:
            log.critical(f"SSH exception when connecting to the County SFTP at {county}!")
            exit(-1)
        except socket.timeout:
            log.critical(f"Timeout connecting to the County SFTP at {county}!")
            exit(-1)
        return destination_filename  # inspection PyShadowingNames
    get_county_file()
    format = "%Y-%m-%d"
    file_path = os.path.join(directory, "all_qss_users.tsv")

    deleteDirectory = (datetime.datetime.strptime(directory, format) - datetime.timedelta(days=1)).strftime(format)

    try:
        import shutil
        shutil.rmtree(deleteDirectory)
    except FileNotFoundError:
        print(f"File {deleteDirectory} most likely already deleted by user or just doesn't exist")


if __name__ == "data.retrieveQSSdata":
    retrieveData()
