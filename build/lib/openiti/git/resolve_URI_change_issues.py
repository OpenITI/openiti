
import re

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(root_folder)

from openiti.git.get_issues import get_issues


def list_issues(repo_name, access_token=None,
               #user=None, password=None,
               issue_labels=None, state="open"):
    issues = get_issues(repo_name,
                        issue_labels=issue_labels,
                        state=state,
                        access_token=access_token)
    issue_list = []
    problematic_issues = []
    for issue in issues:
        #print(issue.title)
        #print(issue.body)
        body = "\n".join(re.split("[ .]*[\r\n]+", issue.body))
        comments = issue.get_comments()
        if comments.totalCount>0:
            comments = [c.body for c in comments]
            #print(comments)
        else:
            comments = []
        
        try: 
            old_uri = re.findall("OLD URI:.*?([a-zA-Z\d.\-]+)\n", body)[0]
            new_uri = re.findall("NEW URI:.*?([a-zA-Z\d.\-]+)\n", body)[0]
            reason = re.findall("REASON:([^\n]+)", body)[0].strip()
            comments = [reason,] + comments

            #print(old_uri, issue.title, old_uri==issue.title.strip())
            #print(new_uri)
            if old_uri==issue.title.strip():
                issue_list.append([str(issue.number),
                                   old_uri,
                                   new_uri,
                                   "::".join(comments),
                                   issue.html_url
                                   ])
        except:
            #print("extraction failed")
            #input("continue?")
            problematic_issues.append(issue)
        #print("***")
    with open("issues.csv", mode="w", encoding="utf-8") as file:
        issues = "\n".join(["\t".join(i) for i in sorted(issue_list)])
        file.write(issues)
        print(issues)
    return issue_list

if __name__ == "__main__": 

    tok_fp = r"D:\London\OpenITI\metadata\automation\kitab-metadata-automation\kitab-metadata-automation\GitHub personalAccessTokenReadOnly.txt"
    with open(tok_fp, mode="r") as file:
        tok = file.read()
    issues = list_issues("OpenITI/Annotation",
                         issue_labels=["URI change suggestion"],
                         state="open", access_token=tok)

    input("Continue?")
    issues = define_text_uris(issues)
    uri_dict = sort_issues_by_uri(issues)
    print_issues_by_uri(uri_dict, "test.tsv")
