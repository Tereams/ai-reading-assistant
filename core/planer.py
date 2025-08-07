import json
from logging_config import logger

def assign_reading_plan(json_file_path: str, total_days: int):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    logger.info(f"Assigning reading plan for: {json_file_path} with total {total_days} days.")
    
    # Set base plan info
    data['has_plan'] = True
    data['planed_date'] = total_days

    chapters = data['metadata']
    total_pages = sum(ch['page_count'] for ch in chapters)
    data['total_page']=total_pages

    # Calculate number of days for each chapter (based on page ratio)
    chapter_days = []
    remaining_days = total_days
    for i, ch in enumerate(chapters):
        if i == len(chapters) - 1:
            days = remaining_days  # Last chapter gets remaining days
        else:
            proportion = ch['page_count'] / total_pages
            days = max(1, round(proportion * total_days))
            remaining_days -= days
        chapter_days.append(days)

    # Assign daily page counts within each chapter
    for ch, days in zip(chapters, chapter_days):
        pages = ch['page_count']
        base_pages_per_day = pages // days
        extra = pages % days

        plan = [base_pages_per_day] * days
        for i in range(extra):
            plan[i] += 1  # Distribute extra pages to early days

        ch['page_per_day'] = plan

    # Save updated plan to file
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Plan successfully assigned. Total pages: {total_pages}, Chapters: {len(chapters)}.")

def advance_plan(json_file_path: str):
    # Load current progress from file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    advanced=data.get('has_advanced', True)
    if advanced:
        logger.info("Plan has already been advanced today. Skipping.")
        return False, 'You have already advanced your plan today.'

    a, b = data.get('current_chapter_plan', [0, 0])
    chapters = data['metadata']

    # Validate chapter index
    if a >= len(chapters):
        logger.warning("Advance failed: Chapter index out of range.")
        return False, "Reading plan completed. No more chapters left."

    # Check if plan exists for current chapter
    current_plan = chapters[a].get("page_per_day")
    if not current_plan:
        logger.warning(f"Advance failed: Chapter {a} has no assigned plan.")
        return False, f"Chapter {a} has no assigned plan. Please generate a plan first."

    if b >= len(current_plan):
        logger.warning(f"Advance failed: Day index out of range for chapter {a}.")
        return False, f"Plan for chapter {a} is already complete."
    
    # Validate plan index
    today_pages = current_plan[b]
    data["current_page"] += today_pages

    # Update reading position
    if b + 1 >= len(current_plan):
        a += 1
        b = 0
    else:
        b += 1

    data["current_chapter_plan"] = [a, b]
    data['has_asked_llm'] = False
    data['has_advanced'] = True
    # Save updated state
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Advanced reading plan. Chapter {a}, Day {b}, +{today_pages} pages.")
    return True, f"You read {today_pages} pages today. Plan advanced to Chapter {a}, Day {b}."


# 示例调用：
if __name__=='__main__':
    assign_reading_plan("metadata/Mere Christianity-Lewis, C_ S.json", 30)
