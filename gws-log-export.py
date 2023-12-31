from google.oauth2 import service_account
from googleapiclient.discovery import build
from loguru import logger
import argparse
import os
from dateutil import tz
from dateutil.parser import parse
import requests
from datetime import datetime, timedelta
from pathlib import Path
import ujson
import sys
import textwrap
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import signal
# from threading import Event
from smart_open import open
def create_parser():
    """
    Function to create an argument parser for the Google Admin SDK reports_v1 API.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """

    parser = argparse.ArgumentParser(
        description="Google Admin SDK reports_v1 API arguments parser"
    )
    parser.add_argument(
        "--credential-file",
        required=True,
        type=str,
        help="Path to the JSON file with Google service account credentials",
    )
    parser.add_argument(
        "--credential-subject",
        required=True,
        type=str,
        help="E-mail of an account to act as to retrieve logs",
    )
    parser.add_argument(
        "--start-date",
        required=True,
        type=valid_date,
        help="Date from which to retrieve the logs, must be formatted as ISO8601 datetime",
    )
    parser.add_argument(
        "--end-date",
        required=False,
        type=valid_date,
        default=datetime.now().isoformat(),
        help="End date for logs retrieval, defaults to current date and time if not provided",
    )
    parser.add_argument(
        "--applications",
        nargs="+",
        default=["login", "admin", "token"],
        help="List of applications for which to retrieve log files",
    )
    parser.add_argument(
        "--all-applications",
        action="store_true",
        help="Flag to select all applications from a list of all known reports_v1 applications",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress outputs as gz",
    )
    parser.add_argument(
        "--show-all-applications",
        action="store_true",
        help="Only display all valid application choices",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Flag to set logging level to debug in the loguru module",
    )
    parser.add_argument(
        "--output-directory",
        required=False,
        type=str,
        default=os.getcwd(),
        help="Directory where to output retrieved data, defaults to current directory if not provided",
    )
    parser.add_argument(
        "--interval",
        required=False,
        type=int,
        default=60*24*7,
        help="Time in minutes into which the logs will be split for retrieval",
    )
    parser.add_argument(
        "--user",
        required=False,
        type=str,
        default='all',
        help="User account to retrieve, defaults to all",
    )
    # parser.add_argument(
    #     "--threads",
    #     required=False,
    #     type=int,
    #     default=1,
    #     help="Number of threads to use to retrieve data",
    # )

    return parser


def valid_date(date_string):
    """
    Function to validate if the date string is in the ISO8601 format.

    Parameters:
        date_string (str): The date string.

    Returns:
        str: The validated date string.
    """

    try:
        date = parse(date_string)
        if date.tzinfo is None:
            print("Warning: No timezone provided, using local timezone")
            date = date.replace(tzinfo=tz.tzlocal())
        return date
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date_string)
        raise argparse.ArgumentTypeError(msg)


def valid_file(file_path):
    """
    Function to validate if the file exists.

    Parameters:
        file_path (str): The file path.

    Returns:
        str: The validated file path.
    """
    if os.path.isfile(file_path):
        return file_path
    else:
        msg = "File does not exist: '{0}'.".format(file_path)
        raise argparse.ArgumentTypeError(msg)


def valid_directory(dir_path):
    """
    Function to validate if the directory exists.

    Parameters:
        dir_path (str): The directory path.

    Returns:
        str: The validated directory path.
    """
    if os.path.isdir(dir_path):
        return dir_path
    else:
        msg = "Directory does not exist: '{0}'.".format(dir_path)
        raise argparse.ArgumentTypeError(msg)

def get_valid_applications():
    logger.debug("Retrieving a list of valid applications from Google APIs")
    r = requests.get('https://admin.googleapis.com/$discovery/rest?version=reports_v1')
    j=r.json()
    names=j['resources']['activities']['methods']['list']['parameters']['applicationName']['enum']
    desc=j['resources']['activities']['methods']['list']['parameters']['applicationName']['enumDescriptions']
    apps=dict(zip(names,desc))
    return apps


def get_intervals(start, end, interval):
    """
    Function to generate datetime pairs which are interval apart

    Parameters:
        start (datetime): Start date and time.
        end (datetime): End date and time.
        interval (int): Interval in minutes.

    Returns:
        List[Tuple[datetime, datetime]]: List of tuples representing datetime pairs.
    """
    # start = datetime.fromisoformat(start)
    # end = datetime.fromisoformat(end)
    interval = timedelta(minutes=interval)

    pairs = []

    while start < end:
        next_time = min(start + interval, end)
        pairs.append((start, next_time))
        start = next_time

    return pairs

def fetch_logs(service,app:str,start_time:datetime,end_time:datetime,user_key,event=None):
    logger.info(f"Retrieving data for app {app} from {start_time.isoformat()} to {end_time.isoformat()} for user {user_key}")
    # logs=[]
    activities = service.activities()
    request = activities.list(
        userKey=user_key, 
        #https://developers.google.com/admin-sdk/reports/reference/rest/v1/activities/list#ApplicationName
        applicationName=app,
        maxResults=1000,
        startTime=start_time.isoformat(),
        endTime=end_time.isoformat(),
        # pageToken=page_token
    )
    while request is not None:
        if event is not None and event.is_set():
            logger.error("Caught exit event")
            return None
        activities_doc = request.execute()
        items=activities_doc.get('items', [])
        if len(items):
            logger.debug(f"Retrieved {len(items)} items, item timestamps are {items[-1]['id']['time']}-{items[0]['id']['time']}")
        for i in items:
            yield i
        request = activities.list_next(request, activities_doc)
    logger.info(f"Completed retrieval for app {app} from {start_time.isoformat()} to {end_time.isoformat()} for user {user_key}")
    # return logs

def do_work(service,a,start,end,user,dest):            
    with open(dest,"w",newline='') as f:
        logs=fetch_logs(service,a,start,end,user)
        for l in logs:
            f.write(ujson.dumps(l)+"\n")


def main():
    parser = create_parser()
    for v in sys.argv:
        if v == "--show-applications":
                all_apps=get_valid_applications()
                for a,d in all_apps.items():
                    wrappde_d="\n".join(textwrap.wrap(d,width=50,subsequent_indent="\t\t"))
                    print(f"{a}\t\t{wrappde_d}")
                return


    args = parser.parse_args()
    all_apps=get_valid_applications()
    apps=[]
    if args.all_applications:
        apps=all_apps.keys()
    else:
        for a in args.applications:
            if a not in all_apps.keys():
                logger.error(f"Application {a} is not a valid choice, valid choices are {all_apps.keys()}")
        apps=args.applications

    credentials = service_account.Credentials.from_service_account_file(
        args.credential_file,
        scopes=["https://www.googleapis.com/auth/admin.reports.audit.readonly"],
    )
    credentials = credentials.with_subject(args.credential_subject)
    service = build('admin', 'reports_v1', credentials=credentials)
    # start_date=
    for a in apps:
        logger.info(f"Starting to retrieve app {a} for user {args.user}")
        # start=args.start_date
        # end=args.end_date
        for start,end in get_intervals(args.start_date,args.end_date,args.interval):
            fn=f"{args.user}-{a}-{start.isoformat().replace(':','')}-{end.isoformat().replace(':','')}"
            if args.compress:
                fn+=".gz"
            dest=Path(args.output_directory) / fn
            # if args.compress:
                # dest=dest / ".gz"
            do_work(service,a,start,end,args.user,dest)
        logger.info(f"Done retrieving app {a} for user {args.user}")



if __name__ == "__main__":
    main()



# Notes: token will only retrieve for 180 days