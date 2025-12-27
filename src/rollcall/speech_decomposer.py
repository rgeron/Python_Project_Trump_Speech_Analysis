import re
def get_title(soup):
    speech_title=soup.find(class_="text-[#2F3C4B] text-center text-xl sm:text-2xl not-italic font-semibold leading-normal sm:leading-9 font-graphik")
    speech_titles=speech_title.get_text(strip=True)
    speech_title=re.search(r"^(.+)-",speech_titles).group(1).strip()
    return speech_title

def get_date(soup):
    speech_title=soup.find(class_="text-[#2F3C4B] text-center text-xl sm:text-2xl not-italic font-semibold leading-normal sm:leading-9 font-graphik")
    speech_titles=speech_title.get_text(strip=True)
    speech_date=re.search(r"-\s(.+)",speech_titles).group(1).strip()
    return speech_date

def get_nbr_sentences_nbr_words_nbr_seconds(soup, candidate_last_name="Trump"):
    blocks_container=soup.find(class_="flex flex-wrap gap-8 justify-between")
    blocks=blocks_container.find_all(class_='flex-1 h-content')
    trump_block=None
    for block in blocks:
        name_div=block.find(class_="font-graphik text-sm font-medium leading-normal flex items-center").get_text(strip=True)
        if candidate_last_name in name_div:
            trump_block=block
    nbr_sentences=""
    nbr_words=""
    nbr_seconds=""
    if trump_block:
        contents=trump_block.find_all(class_="font-graphik text-xs font-medium text-[#2F3C4B]")
        contents=[content.get_text(strip=True) for content in contents]
        for content in contents :
            if "sentences" in content:
                nbr_sentences=re.search(r'\d+',content).group()
            elif "words" in content:
                nbr_words=re.search(r'\d+',content).group()
            else :
                nbr_seconds=re.search(r'\d+',content).group()
    return [nbr_sentences,nbr_words,nbr_seconds]

def get_cleaned_categories(soup):
    categories=soup.find_all(class_="text-[#015582] text-sm font-normal leading-normal rounded-md bg-[#F4F4F5] border border-[#D9D9D9] p-2")
    categories=[category.get_text(strip=True) for category in categories]
    categories=[category.split('>') for category in categories]
    categories=list(set([category[i].strip() for category in categories for i in range(len(category))]))
    return categories

def get_candidate_transcriptions(soup, candidate_full_name="Donald Trump"):
    transcriptions=soup.find_all(class_='flex gap-4 py-2')
    list_transcriptions=[]
    for transcription in transcriptions :
        speaker=transcription.find(class_="text-md inline").get_text(strip=True)
        try : timestamp=transcription.find(class_='text-xs text-gray-600 inline ml-2').get_text(strip=True) #certains speech n'ont pas de timestamp
        except : timestamp=""
        text=transcription.find(class_='flex-auto text-md text-gray-600 leading-loose').get_text(strip=True)
        list_transcriptions.append([speaker,timestamp,text])
    trump_transcriptions=[transcription_list[1:] for transcription_list in list_transcriptions if candidate_full_name in transcription_list[0]]
    return trump_transcriptions



