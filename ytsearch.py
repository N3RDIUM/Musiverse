from youtube_search import YoutubeSearch
results = YoutubeSearch('noboilerplate', max_results=10).to_dict()
print(results)