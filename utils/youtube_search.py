import requests
import json
import re
from googleapiclient.discovery import build
from configs import configs


class YoutubeVideo:
    """Temporary class that holds a youtube video's information for searches """
    def __init__(self, vid, title, duration):
        self.id = vid
        self.url = "https://www.youtube.com/watch?v=" + self.id
        self.title = title
        self.duration = duration

    def __str__(self):
        fmt = "{0} [{1}]".format(self.title, self.duration)
        return fmt

    def get_id(self):
        return self.id

    def get_url(self):
        return self.url

    def get_title(self):
        return self.title

    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration


class YouTubeSearch:
    """ This class uses Youtube's API to search for videos """
    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=configs.YOUTUBE_API_KEY)

    def search_youtube(self, term):
        """ This method searches youtube using given term query and returns a list with five YoutubeVideo objects"""
        try:
            videos = []
            ids = []
            search_response = self.youtube.search().list(
                q=term,
                type="video",
                part="id, snippet",
                maxResults=configs.YOUTUBE_DEFAULT_SEARCH_RETURNS,
                safeSearch="none"
              ).execute()

            for search_result in search_response.get("items", []):
                ids.append(search_result["id"]["videoId"])

            # Youtube API doesn't return duration with the search results, so we have to query it through
            # google's separate search API
            duration = self._get_duration(ids) # list of video durations in order

            for search_result, dur in zip(search_response.get("items", []), duration):
                videos.append(YoutubeVideo(search_result["id"]["videoId"],
                                            search_result["snippet"]["title"], dur))

            return videos
        except Exception as e:
            print(e)
            return [] # PEP says empty array returns as false

    @staticmethod
    def get_metadata(url):
        id_string = ''
        if 'youtube' in url:
            id_string = re.search(r"youtube\.com/.*v=([^&]*)", url).group(1)
        elif 'youtu.be' in url: # shortened links
            id_string = re.search(r"youtu.be/([^&]*)", url).group(1)
        url = "https://www.googleapis.com/youtube/v3/videos?id="\
            + id_string + "&key=" + configs.YOUTUBE_API_KEY + "&part=snippet,contentDetails"

        video = None

        try:
            details = json.loads(requests.get(url).text)
            dur = details['items'][0]['contentDetails']['duration']
            duration = re.sub(r"(\d{0,2}\w?)(\d{0,2}\w?)(\d{0,2}\w?)", r"\1 \2 \3", dur[2:])
            video = YoutubeVideo(details['items'][0]['id'],
                                 details['items'][0]['snippet']['title'],
                                 duration.rstrip())
        except Exception as e:
            print(type(e).__name__, '\n',e)
            pass

        return video

    @staticmethod
    def _get_duration(ids):
        duration = []

        # maximum number of ids per call is 50, so we have to split it
        if len(ids) > 50:
            split_ids = [ids[x:x+50] for x in range(0, len(ids), 50)]
            string_urls = []
            for vid in split_ids:
                string_urls.append(','.join(vid))

            for url in string_urls:
                search_url = "https://www.googleapis.com/youtube/v3/videos?id="\
                    + url + "&key=" + configs.YOUTUBE_API_KEY + \
                    "&part=contentDetails"
                # print(search_url)
                details = json.loads(requests.get(search_url).text)

                for dur_idx in details.get('items', []):
                    duration_string = dur_idx['contentDetails']['duration']

                    # the duration string is in ISO 8601 format ( PT#H#M#S, ex:PT1H2M3S ) so we will convert it
                    # to #H #M #S format ( PT1H2M3S -> 1H 2M 3S ) using regex
                    duration_string_filtered = re.sub(r"(\d{0,2}\w?)(\d{0,2}\w?)(\d{0,2}\w?)", r"\1 \2 \3",
                                                      (duration_string[2:]))
                    duration.append(duration_string_filtered.rstrip())

        else:
            id_string = ','.join(ids)

            # Google APIs URL call using ids and the API key
            url = "https://www.googleapis.com/youtube/v3/videos?id="\
                + id_string + "&key=" + configs.YOUTUBE_API_KEY + \
                  "&part=contentDetails"
            # print(url)
            # Convert url to json format for reading
            details = json.loads(requests.get(url).text)

            # Getting the duration from the json
            for dur_idx in details.get('items', []):

                duration_string = dur_idx['contentDetails']['duration']

                # the duration string is in ISO 8601 format ( PT#H#M#S, ex:PT1H2M3S ) so we will convert it
                # to #H #M #S format ( PT1H2M3S -> 1H 2M 3S ) using regex
                duration_string_filtered = re.sub(r"(\d{0,2}\w?)(\d{0,2}\w?)(\d{0,2}\w?)", r"\1 \2 \3",
                                                  (duration_string[2:]))
                duration.append(duration_string_filtered.rstrip())

        return duration

    def get_playlist_videos(self, playlist_url):
        """ This method returns a list of YoutubeVideo objects that is in the given playlist URL"""
        # Get the playlist ID from the url
        # print(playlist_url)
        playlist_id = re.search(r"youtube\.com/.*list=([^&]*)", playlist_url).group(1)

        # Getting the videos
        # Note that Youtube API only returns 50 at a time so we have to use nextPageToken to
        # go to the next page.
        res = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=configs.YOUTUBE_MAX_SEARCH_RETURNS
            ).execute()

        nextPageToken = res.get('nextPageToken')

        while 'nextPageToken' in res:

            nextPage = self.youtube.playlistItems().list(
            part="snippet",
            playlistId= playlist_id,
            maxResults=configs.YOUTUBE_MAX_SEARCH_RETURNS,
            pageToken=nextPageToken
            ).execute()

            res['items'] = res['items'] + nextPage['items']

            if 'nextPageToken' not in nextPage:
                res.pop('nextPageToken', None)
            else:
                nextPageToken = nextPage['nextPageToken']

        # getting video info and ids for search
        ids = []
        for items in res['items']:
            # check if video is available first
            if not ('deleted' in items['snippet']['title'].lower() or
                    'private' in items['snippet']['title'].lower()):

                # adding the videos
                ids.append(items['snippet']['resourceId']['videoId'])

        return self._get_duration_for_playlists(ids)

    def _get_duration_for_playlists(self, ids):
        # Sometimes Youtube API return a deleted video's true information instead of renaming the title to deleted.
        # This mess up the regular duration search so in this case, we will return a dict of the ids and duration
        # to filter em out
        playlist_videos = []

        # maximum number of ids per call is 50, so we have to split it
        if len(ids) > 50:
            split_ids = [ids[x:x+50] for x in range(0, len(ids), 50)]
            string_urls = []
            for vid in split_ids:
                string_urls.append(','.join(vid))

            for url in string_urls:
                search_url = "https://www.googleapis.com/youtube/v3/videos?id="\
                    + url + "&key=" + configs.YOUTUBE_API_KEY + \
                    "&part=snippet,contentDetails"
                # print(search_url)
                details = json.loads(requests.get(search_url).text)

                for item in details.get('items', []):
                    duration_string = item['contentDetails']['duration']

                    # the duration string is in ISO 8601 format ( PT#H#M#S, ex:PT1H2M3S ) so we will convert it
                    # to #H #M #S format ( PT1H2M3S -> 1H 2M 3S ) using regex
                    duration_string_filtered = re.sub(r"(\d{0,2}\w?)(\d{0,2}\w?)(\d{0,2}\w?)", r"\1 \2 \3",
                                                      (duration_string[2:]))

                    playlist_videos.append(YoutubeVideo(item['id'],
                                                        item['snippet']['localized']['title'],
                                                        duration_string_filtered.rstrip()))

        else:
            id_string = ','.join(ids)

            # Google APIs URL call using ids and the API key
            url = "https://www.googleapis.com/youtube/v3/videos?id="\
                + id_string + "&key=" + configs.YOUTUBE_API_KEY + \
                  "&part=snippet,contentDetails"
            # print(url)
            # Convert url to json format for reading
            details = json.loads(requests.get(url).text)

            # Getting the duration from the json
            for item in details.get('items', []):

                duration_string = item['contentDetails']['duration']

                # the duration string is in ISO 8601 format ( PT#H#M#S, ex:PT1H2M3S ) so we will convert it
                # to #H #M #S format ( PT1H2M3S -> 1H 2M 3S ) using regex
                duration_string_filtered = re.sub(r"(\d{0,2}\w?)(\d{0,2}\w?)(\d{0,2}\w?)", r"\1 \2 \3",
                                                  (duration_string[2:]))
                playlist_videos.append(YoutubeVideo(item['id'],
                                                    item['snippet']['localized']['title'],
                                                    duration_string_filtered.rstrip()))

        return playlist_videos
