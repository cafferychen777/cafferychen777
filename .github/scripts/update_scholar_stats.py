#!/usr/bin/env python3
"""
Update Google Scholar statistics in README.md
"""

import re
import time
from scholarly import scholarly

# 您的Google Scholar ID
SCHOLAR_ID = "I6BPn-IAAAAJ"

def get_scholar_stats():
    """获取Google Scholar统计数据"""
    try:
        # 获取作者信息
        author = scholarly.search_author_id(SCHOLAR_ID)
        scholarly.fill(author)
        
        # 获取统计数据
        stats = {
            'citations': author['citedby'],
            'h_index': author['hindex'],
            'i10_index': author['i10index'],
            'publications': len(author['publications'])
        }
        
        # 获取前5篇引用最多的论文
        top_papers = []
        sorted_pubs = sorted(author['publications'], 
                            key=lambda x: x['num_citations'] if 'num_citations' in x else 0, 
                            reverse=True)
        
        count = 0
        for pub in sorted_pubs:
            if count >= 5:
                break
                
            try:
                scholarly.fill(pub)
                top_papers.append({
                    'title': pub['bib']['title'],
                    'citations': pub['num_citations'] if 'num_citations' in pub else 0,
                    'year': pub['bib']['pub_year'] if 'pub_year' in pub['bib'] else 'N/A',
                    'venue': pub['bib']['venue'] if 'venue' in pub['bib'] else 'N/A'
                })
                count += 1
                # 避免请求过快被封
                time.sleep(1)
            except Exception as e:
                print(f"Error filling publication details: {e}")
                continue
        
        return stats, top_papers
    
    except Exception as e:
        print(f"Error fetching Google Scholar data: {e}")
        return None, None

def update_readme(stats, top_papers):
    """更新README.md文件中的Google Scholar统计数据"""
    try:
        with open('README.md', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 检查是否已有Scholar Stats部分
        scholar_section = re.search(r'## Google Scholar Stats.*?(?=##|\Z)', content, re.DOTALL)
        
        # 创建新的Scholar Stats部分
        new_section = f"""## Google Scholar Stats

![Citations](https://img.shields.io/badge/Citations-{stats['citations']}-blue?style=for-the-badge&logo=google-scholar&logoColor=white)
![h-index](https://img.shields.io/badge/h--index-{stats['h_index']}-blue?style=for-the-badge&logo=google-scholar&logoColor=white)
![i10-index](https://img.shields.io/badge/i10--index-{stats['i10_index']}-blue?style=for-the-badge&logo=google-scholar&logoColor=white)
![Publications](https://img.shields.io/badge/Publications-{stats['publications']}-blue?style=for-the-badge&logo=google-scholar&logoColor=white)

### Top Cited Papers
"""
        
        # 添加引用最多的论文
        for paper in top_papers:
            new_section += f"- **{paper['title']}** ({paper['year']}, {paper['venue']}) - {paper['citations']} citations\n"
        
        new_section += "\n"
        
        # 更新README内容
        if scholar_section:
            # 替换现有部分
            updated_content = content.replace(scholar_section.group(0), new_section)
        else:
            # 在Connect with me部分前添加
            connect_section = re.search(r'## Connect with me', content)
            if connect_section:
                updated_content = content[:connect_section.start()] + new_section + content[connect_section.start():]
            else:
                # 如果没有Connect with me部分，添加到文件末尾
                updated_content = content + "\n" + new_section
        
        # 写入更新后的内容
        with open('README.md', 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        print("README.md updated successfully with Google Scholar stats")
        return True
        
    except Exception as e:
        print(f"Error updating README.md: {e}")
        return False

def main():
    """主函数"""
    stats, top_papers = get_scholar_stats()
    if stats and top_papers:
        update_readme(stats, top_papers)
    else:
        print("Failed to update README.md: Could not fetch Google Scholar data")

if __name__ == "__main__":
    main()
