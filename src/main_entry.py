from src.bag_crawler import BagCrawler

def main_entry(args):
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
    return {"status":"ok"}
