import os
import sys
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pickle
import requests


class Api:
    
    def __init__(self, c_secret_file, scopes, oauth_file, playlist_name, api_service_name = "youtube", api_version = "v3"):
        self.playlist_name = playlist_name

        credentials = self.get_oauth(c_secret_file, scopes, oauth_file)
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

    def send_request(self,request):
        response = ""
        try:
            response = request.execute()
        except:
            print("Unexpected error:", sys.exc_info()[0])
            response = sys.exc_info()[0]

        return response
    

    def get_oauth(self, client_secrets_file, scopes, oauth_file):
        if(os.path.exists(oauth_file)):
            with open(oauth_file, 'rb') as ofile:
                return pickle.load(ofile)
        
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        with open(oauth_file, 'wb') as ofile:
            pickle.dump(credentials, ofile)
        return credentials

    def get_my_playlists(self):

        request = self.youtube.playlists().list(
            part="snippet,contentDetails",
            maxResults=50,
            mine=True
        )
        response = self.send_request(request)
        return response

    def create_new_playlist(self,title):

        request = self.youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                 },
                 "status": {
                     "privacyStatus":"public"
                 }
            }
        )
        response = self.send_request(request)
        return response

    def add(self, video_id):
        playlists = self.get_my_playlists()
        playlist_id = 0
        for plist in playlists['items']:
            if(plist['snippet']['title'] == self.playlist_name and plist['contentDetails']['itemCount']<5000):
                playlist_id = plist['id']
                break

        if(playlist_id == 0):
            print("creating new")
            res = self.create_new_playlist(self.playlist_name)
            playlist_id = res['id']

        self.add_video_to_playlist(video_id, playlist_id)
        

    def add_video_to_playlist(self, video_id, playlist_id):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        

        request = self.youtube.playlistItems().insert(
            part="snippet",
            body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId":{
                    "kind": "youtube#video",
                    "videoId":video_id,
                    }
                }
            }
        )
        response = self.send_request(request)

        try:
            print(response['snippet']['title'])
        except:
            pass

        return response
