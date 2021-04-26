import sys
from .bag_faq_crawler import BagFaqCrawler

if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) != 4:
        print("This script requires exactly four command-line arguments!")
        print("[watson_api_key] [watson_skill_id] [watson_workspace_url] [bag_faq_url]")
        exit(1)
    watson_api_key = args[0]
    watson_skill_id = args[1]
    watson_workspace_url = args[2]
    bag_faq_url = args[3]
    if "v1/workspaces" in watson_workspace_url:
        print("Remove \"/v1/workspaces/.../message\" at the end of the workspace url")
        exit(1)
    BagFaqCrawler(watson_api_key,watson_skill_id,watson_workspace_url,bag_faq_url).crawl()



else:
    raise ImportError("Run this file directly, don't import it!")
