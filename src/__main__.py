import sys
from src.bag_crawler import BagCrawler

def main(args):
    if len(args) != 5:
        print("This script requires exactly five arguments!")
        print("[watson_api_key] [watson_skill_id] [watson_workspace_url] [bag_faq_url] [vaccination_center_url]")
        exit(1)
    watson_api_key = args['watson_api_key']
    watson_skill_id = args['watson_skill_id']
    watson_workspace_url = args['watson_workspace_url']
    bag_faq_url = args['bag_faq_url']
    vaccination_center_url = args['vaccination_center_url']
    if "v1/workspaces" in watson_workspace_url:
        print("Remove \"/v1/workspaces/.../message\" at the end of the workspace url")
        exit(1)
    BagCrawler(watson_api_key, watson_skill_id, watson_workspace_url, bag_faq_url, vaccination_center_url).crawl()

if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) != 5:
        main({})
    else:
        main({'watson_api_key':args[0],'watson_skill_id':args[1],'watson_workspace_url':args[2],'bag_faq_url':args[3], 'vaccination_center_url':args[4]})

else:
    raise ImportError("Run this file directly, don't import it!")
