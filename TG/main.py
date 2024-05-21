from pyexpat import model
import tkinter as tk
from tkinter import ttk, PhotoImage
import customtkinter as ctk
from CTkTable import *  # type: ignore
from PIL import Image
import time
import pandas as pd
from transformers import pipeline, Pipeline
import lyricsgenius as lg
from dotenv import load_dotenv
import os
from os import getenv
import sys
from typing import List, Dict, Optional, Any, Callable, Literal, Sequence
from imdb import IMDb
from json import dumps
import nltk
from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
# from nltk.stem import WordNetLemmatizer


Oblivion = r"Oblivion.json"
with open("launch.txt", "r") as f:
    global launch_appearance
    launch_appearance = f.readlines()[-1]
match launch_appearance:
    case x if x == "Oblivion":
        ctk.set_default_color_theme(Oblivion)
    case y if y == "blue":
        ctk.set_default_color_theme("blue")
    case z if z == "green":
        ctk.set_default_color_theme("green")
    case i if i == "dark-blue":
        ctk.set_default_color_theme("dark-blue")
    case _:
        ctk.set_default_color_theme(Oblivion)


ctk.set_appearance_mode("System")
ctk.set_widget_scaling(1)


def MyTheme():
    global Oblivion
    Oblivion = {
        "CTk": {"fg_color": ["#c3cbd5", "#495157"]},
        "CTkToplevel": {"fg_color": ["#181b28", "#181b28"]},
        "CTkFrame": {
            "corner_radius": 6,
            "border_width": 0,
            "fg_color": ["#7e8fa5", "#262e34"],
            "top_fg_color": ["#5b6c82", "#181b28"],
            "border_color": ["#10121f", "#1b303d"],
        },
        "CTkButton": {
            "corner_radius": 6,
            "border_width": 0,
            "fg_color": ["#303344", "#1a3c5a"],
            "hover_color": ["#444653", "#0d0f1c"],
            "border_color": ["#080b12", "#001162"],
            "text_color": ["#ffffff", "#cdc8ce"],
            "text_color_disabled": ["#9a9a9a", "#7a8894"],
        },
        "CTkLabel": {
            "corner_radius": 0,
            "fg_color": "transparent",
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "text_color_disabled": ["#cdc8ce", "#cdc8ce"],
        },
        "CTkEntry": {
            "corner_radius": 6,
            "border_width": 2,
            "fg_color": ["#3f4253", "#212435"],
            "border_color": ["#080b12", "#001162"],
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "placeholder_text_color": ["#cdc8ce", "#cdc8ce"],
        },
        "CTkSwitch": {
            "corner_radius": 1000,
            "border_width": 3,
            "button_length": 0,
            "fg_Color": [None, None],
            "progress_color": ["#2854bb", "#1e2473"],
            "button_color": ["#2e324a", "#2e324a"],
            "button_hover_color": ["#2e324a", "#2e324a"],
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "text_color_disabled": ["#7a8894", "#7a8894"],
            "fg_color": ["#1f2233", "#1f2233"],
        },
        "CTkProgressBar": {
            "corner_radius": 1000,
            "border_width": 0,
            "fg_color": ["#0a369d", "#001162"],
            "progress_color": ["#363844", "#363844"],
            "border_color": ["#0d101f", "#1b303d"],
        },
        "CTkSlider": {
            "corner_radius": 1000,
            "button_corner_radius": 1000,
            "border_width": 6,
            "button_length": 0,
            "fg_color": ["#2854bb", "#1e2473"],
            "progress_color": ["#363844", "#363844"],
            "button_color": ["#303344", "#303344"],
            "button_hover_color": ["#10121f", "#10121f"],
        },
        "CTkOptionMenu": {
            "corner_radius": 6,
            "fg_color": ["gray20", "gray20"],
            "button_color": ["#144870", "#144870"],
            "button_hover_color": ["#203A4F", "#203A4F"],
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "text_color_disabled": ["#7a8894", "#7a8894"],
        },
        "CTkComboBox": {
            "corner_radius": 6,
            "border_width": 2,
            "fg_color": ["gray20", "gray20"],
            "border_color": ["#565B5E", "#001162"],
            "button_color": ["#444758", "#212435"],
            "button_hover_color": ["#7A848D", "#7A848D"],
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "text_color_disabled": ["#7a8894", "#7a8894"],
        },
        "CTkScrollbar": {
            "corner_radius": 1000,
            "border_spacing": 4,
            "fg_color": "transparent",
            "button_color": ["gray41", "#141623"],
            "button_hover_color": ["gray53", "#4a4f6a"],
        },
        "CTkSegmentedButton": {
            "corner_radius": 6,
            "border_width": 2,
            "fg_color": ["#11536c", "#212435"],
            "selected_color": ["#262835", "#262835"],
            "selected_hover_color": ["#313449", "#313449"],
            "unselected_color": ["#181b28", "#181b28"],
            "unselected_hover_color": ["#313449", "#313449"],
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "text_color_disabled": ["#7a8894", "#7a8894"],
        },
        "CTkTextbox": {
            "corner_radius": 6,
            "border_width": 0,
            "fg_color": ["#3f4253", "#26293a"],
            "border_color": ["#080b12", "#001162"],
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "scrollbar_button_color": ["#696969", "#696969"],
            "scrollbar_button_hover_color": ["#878787", "#878787"],
        },
        "CTkScrollableFrame": {"label_fg_color": ["#181b28", "#0e2034"]},
        "DropdownMenu": {
            "fg_color": ["gray20", "gray20"],
            "hover_color": ["gray28", "gray28"],
            "text_color": ["#DCE4EE", "#DCE4EE"],
        },
        "CTkFont": {
            "macOS": {"family": "SF Display", "size": 13, "weight": "normal"},
            "Windows": {"family": "Roboto", "size": 13, "weight": "normal"},
            "Linux": {"family": "Roboto", "size": 13, "weight": "normal"},
        },
        "CTkCheckBox": {
            "corner_radius": 6,
            "border_width": 3,
            "fg_color": ["#212435", "#212435"],
            "border_color": ["#01e9c4", "#001162"],
            "hover_color": ["#171926", "#171926"],
            "checkmark_color": ["#3965fd", "#01e9c4"],
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "text_color_disabled": ["#7a8894", "#7a8894"],
        },
        "CTkRadioButton": {
            "corner_radius": 1000,
            "border_width_checked": 6,
            "border_width_unchecked": 3,
            "fg_color": ["#0a369d", "#28398a"],
            "border_color": ["#2b2e3f", "#1b303d"],
            "hover_color": ["#10121f", "#10121f"],
            "text_color": ["#cdc8ce", "#cdc8ce"],
            "text_color_disabled": ["#7a8894", "#7a8894"],
        },
        "provenance": {
            "theme name": "Sweetkind",
            "theme author": "@Akascape",
            "date created": "Aug 16 2023 11:56:06",
            "last modified by": "monta",
            "last modified": "May 20 2024 02:18:32",
            "created with": "CTk Theme Builder v2.4.0",
            "keystone colour": "#181b28",
            "harmony method": "Triadic",
            "harmony differential": 5,
        },
    }
    return dumps(Oblivion)


# --------------------------------------------------------------------------------#


# Custom Data Structures:
API = str | Any
SongSearch = str | bool
Genius = lg.Genius
Lyrics = str | Literal[True]


CStructIMDb = Any
MovieName = str | int | float
MovieSearch = Sequence[Any]
Movie = Any
Reviews = List[Dict[str, str]]


# --------------------------------------------------------------------------------#


# The Model:
def WakeUpRoBERTa() -> Pipeline:
    RoBERTa = pipeline(
        task="sentiment-analysis",
        model="SamLowe/roberta-base-go_emotions",
        top_k=None,
    )
    return RoBERTa


def ParseSentece(sentence: str) -> list[str]:
    sentenceParsed = preprocess_text(sentence)
    sentenceParsed: list[str] = [sentence]
    return sentenceParsed


def GetSentenceAnalysis(sentenceParsed: list[str], model: Pipeline) -> dict[str, float]:
    sentenceAnalysis: list[dict[str, float]] = model(sentenceParsed)  # type: ignore
    return sentenceAnalysis[0]


def MakeSentimentAnalysisDataFrame(sentimentAnalysis: dict[str, float]) -> pd.DataFrame:
    sentimentAnalysisDataFrame: pd.DataFrame = pd.DataFrame(
        sentimentAnalysis,
    )
    return sentimentAnalysisDataFrame


# --------------------------------------------------------------------------------#


def GetCurrentTime():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(f"{current_time}")


# --------------------------------------------------------------------------------#


# The Lyrics Genius API:
def GetAPIToken() -> API:
    load_dotenv(override=True)
    tokenToken: API = getenv("GENIUS_ACCESS_TOKEN")
    return tokenToken


def ParseLyricsGeniusRequest() -> Lyrics:
    tokenToken: API = GetAPIToken()
    nameArtist: str = SongLyricsPageArtistEntry.get()
    nameSong: str = SongLyricsPageSongEntry.get()
    lyrics = GetLyrics(tokenToken, nameArtist, nameSong)
    msgError: str = "Lyrics not found"
    return lyrics if lyrics else msgError


def GetLyrics(tokenToken: API, nameArtist: str, nameSong: str) -> SongSearch:
    genius: Genius = lg.Genius(tokenToken)
    song = genius.search_song(nameSong, nameArtist)
    return song.lyrics if song else False


def CleanLyrics(lyrics: Lyrics) -> str:
    lyricsList: List[str] = lyrics.split("\n")  # type: ignore
    del lyricsList[0]
    lyricsClean = " ".join(
        [line for line in lyricsList if not line.startswith("[") or line != ""]
    )
    lyricsClean = lyricsClean[:-8]
    return lyricsClean


# --------------------------------------------------------------------------------#


# IMDb Movie Review API
def InitializeIMDbAPI() -> CStructIMDb:
    ia: CStructIMDb = IMDb()
    return ia


def FetchMovieSearchResults(ia: CStructIMDb, nameMovie: MovieName) -> MovieSearch:
    results: MovieSearch = ia.search_movie(nameMovie)
    return results


def SelectMovieFromSearchResults(results: MovieSearch) -> Movie:
    movie: Movie = results[0]
    return movie


def UpdateAPIToIncludeReviews(ia: CStructIMDb, movie: Movie) -> None:
    ia.update(movie, ["reviews"])


def SelectReviews(movie: Movie) -> Reviews:
    reviews: Reviews = movie["reviews"]
    return reviews


# --------------------------------------------------------------------------------#


def preprocess_text(text):
  return ' '.join([word.lower() for word in nltk.word_tokenize(text)])


# def Tokenizer(sentence: str):
#     nltk.download("punkt")
#     nltk.download("stopwords")
#     sentence = word_tokenize(sentence)
# 
#     stop_words = set(stopwords.words("english"))
#     # stop_words.update({';', ',', '.', ':'}) # for add stop word from the list
#     # stop_words.discard({'I', 'not'}) # for delet stop word from the list
# 
#     filtered_list = []
#     for word in sentence:
#         if word.casefold() not in stop_words:
#             filtered_list.append(word)
# 
#     stemmer = PorterStemmer()
#     stemmed_words = [stemmer.stem(word) for word in filtered_list]
#     nltk.download("wordnet")
#     lemmatizer = WordNetLemmatizer()
#     lemmatizer.lemmatize("scarves")
#     nltk.download("averaged_perceptron_tagger")
#     nltk.download("tagsets")


# --------------------------------------------------------------------------------#


# Event Handler functions:
# Home Navigation Button Event Handler:
def HomePageNavigationButtonEventHandler():
    # Print Event to Console:
    GetCurrentTime()
    print("HomePageNavigationButtonPressed")

    # Clearing The MainFrame
    print("MainFrameGridPagesForgetCalling")
    MainFrameGridPagesForget()
    print("MainFrameGridPagesForgetCalled")

    # Call the Display Function:
    print("MainFramePgeDisplayCallingOnHomePage")
    MainFramePageDisplay(HomePage)
    print("MainFramePageDisplayCalledOnHomePage")
    print("EventLogOutputFinished")
    GetCurrentTime()
    print("\n")


# Model Navigation Button Event Handler:
def ModelPageNavigationButtonEventHandler():
    # Print Event to Console:
    GetCurrentTime()
    print("ModelPageNavigationButtonPressed")

    # Clearing The MainFrame
    print("MainFrameGridPagesForgetCalling")
    MainFrameGridPagesForget()
    print("MainFrameGridPagesForgetCalled")

    # Call the Display Function:
    print("MainFramePgeDisplayCallingOnModelPage")
    MainFramePageDisplay(ModelPage)
    print("MainFramePageDisplayCalledOnModelPage")
    print("EventLogOutputFinished")
    GetCurrentTime()
    print("\n")


# Song Lyrics Navigation Button Event Handler:
def SongLyricsPageNavigationButtonEventHandler():
    # Print Event to Console:
    GetCurrentTime()
    print("SongLyricsPageNavigationButtonPressed")

    # Clearing The MainFrame
    print("MainFrameGridPagesForgetCalling")
    MainFrameGridPagesForget()
    print("MainFrameGridPagesForgetCalled")

    # Call the Display Function:
    print("MainFramePgeDisplayCallingOnSongLyricsPage")
    MainFramePageDisplay(SongLyricsPage)
    print("MainFramePageDisplayCalledOnSongLyricsPage")
    print("EventLogOutputFinished")
    GetCurrentTime()
    print("\n")


# Movie Reviews Navigation Button Event Handler:
def MovieReviewsPageNavigationButtonEventHandler():
    # Print Event to Console:
    GetCurrentTime()
    print("MovieReviewsPageNavigationButtonPressed")

    # Clearing The MainFrame
    print("MainFrameGridPagesForgetCalling")
    MainFrameGridPagesForget()
    print("MainFrameGridPagesForgetCalled")

    # Call the Display Function:
    print("MainFramePgeDisplayCallingOnMovieReviewsPage")
    MainFramePageDisplay(MovieReviewsPage)
    print("MainFramePageDisplayCalledOnMovieReviewsPage")
    print("EventLogOutputFinished")
    GetCurrentTime()
    print("\n")


# Url Navigation Button Event Handler:
def UrlPageNavigationButtonEventHandler():
    # Print Event to Console:
    GetCurrentTime()
    print("UrlPageNavigationButtonPressed")

    # Clearing The MainFrame
    print("MainFrameGridPagesForgetCalling")
    MainFrameGridPagesForget()
    print("MainFrameGridPagesForgetCalled")

    # Call the Display Function:
    print("MainFramePgeDisplayCallingOnUrlPage")
    MainFramePageDisplay(UrlPage)
    print("MainFramePageDisplayCalledOnUrlPage")
    print("EventLogOutputFinished")
    GetCurrentTime()
    print("\n")


# Settings Navigation Button Event Handler:
def SettingsPageNavigationButtonEventHandler():
    # Print Event to Console:
    GetCurrentTime()
    print("SettingsPageNavigationButtonPressed")

    # Clearing The MainFrame
    print("MainFrameGridPagesForgetCalling")
    MainFrameGridPagesForget()
    print("MainFrameGridPagesForgetCalled")

    # Call the Display Function:
    print("MainFramePgeDisplayCallingOnSettingsPage")
    MainFramePageDisplay(SettingsPage)
    print("MainFramePageDisplayCalledOnSettingsPage")
    print("EventLogOutputFinished")
    GetCurrentTime()
    print("\n")


def ModelPageAnalyzeButtonEventHandler():
    TextToAnalyze = ModelTextBoxInput.get(0.0, "end")
    TextToAnalyzeParsed = ParseSentece(TextToAnalyze)
    AnalyzedText = GetSentenceAnalysis(TextToAnalyzeParsed, Model)
    AnalyzedTextDataFrame = MakeSentimentAnalysisDataFrame(AnalyzedText)
    ModelTableOutputDisplayModelOutput(AnalyzedTextDataFrame)


def SongLyricsPageGetLyricsButtonEventHandler():
    Lyrics = ParseLyricsGeniusRequest()

    global LyricsClean
    LyricsClean = CleanLyrics(Lyrics)

    SongLyricsPageOutputTextBox.configure(
        state="normal",
    )
    SongLyricsPageOutputTextBox.insert(
        0.0,
        LyricsClean,
    )
    SongLyricsPageOutputTextBox.configure(
        state="disabled",
    )


def SongLyricsPageAnalyzeLyricsButtonEventHandler():
    ParsedLyrics = ParseSentece(LyricsClean)
    LyricsSentimentAnalyses = GetSentenceAnalysis(
        ParsedLyrics,
        model=Model,
    )
    LyricsSentimentAnalysesDataFrame = MakeSentimentAnalysisDataFrame(
        LyricsSentimentAnalyses,
    )
    SongLyricsPageTableDisplaySentimentAnalysesDataFrame(
        LyricsSentimentAnalysesDataFrame
    )


def SongLyricsPageSentimentAnalysesOutputTableClearButtonEventHandler():
    SongLyricsPageSentimentAnalysesOutputTableTable.update_values(
        values=[],
    )
    SongLyricsPageOutputTextBox.configure(
        state="normal",
    )
    SongLyricsPageOutputTextBox.delete(
        0.0,
        "end",
    )
    SongLyricsPageOutputTextBox.configure(
        state="disabled",
    )


def MovieReviewsPageGetReviewButtonEventHandler():
    ia = InitializeIMDbAPI()
    MovieName = MovieReviewsPageMovieEntry.get()
    MovieSearchResults = FetchMovieSearchResults(
        ia,
        MovieName,
    )
    MovieMovie = SelectMovieFromSearchResults(MovieSearchResults)
    UpdateAPIToIncludeReviews(
        ia,
        MovieMovie,
    )
    global MovieReviews
    MovieReviews = SelectReviews(MovieMovie)
    MovieReviewsClean = [
        f"{review['content'][:250]}...\n{'-' * 48}" for review in MovieReviews[:10]
    ]

    MovieReviewsPageReviesTextBox.configure(
        state="normal",
    )
    MovieReviewsPageReviesTextBox.insert(
        0.0,
        MovieReviewsClean,
    )
    MovieReviewsPageReviesTextBox.configure(
        state="disable",
    )


def MovieReviewsPageAnalyzeButtonEventHandler():
    MoviewReviewsReadyForSentimentAnalysesProsses = "\n".join(
        [f"{review['content'][:200]} " for review in MovieReviews[:10]]
    )
    ReviewsParsed = ParseSentece(MoviewReviewsReadyForSentimentAnalysesProsses)
    ReviewsSentimentAnalyses = GetSentenceAnalysis(
        ReviewsParsed,
        model=Model,
    )
    ReviewsSentimentAnalysesDataFrame = MakeSentimentAnalysisDataFrame(
        ReviewsSentimentAnalyses,
    )
    MovieReviewsSentimentAnalysesOutputTableTable.update_values(
        values=[
            item.insert(0, idx + 1) or item
            for idx, item in enumerate(
                ReviewsSentimentAnalysesDataFrame.to_numpy().tolist()[:10]
            )
        ]
    )


def MovieReviewsPageSentimentAnalysesTableClearButtonEventHandler():
    MovieReviewsSentimentAnalysesOutputTableTable.update_values(
        values=[],
    )
    MovieReviewsPageReviesTextBox.configure(
        state="normal",
    )
    MovieReviewsPageReviesTextBox.delete(
        0.0,
        "end",
    )
    MovieReviewsPageReviesTextBox.configure(
        state="disable",
    )


def SettingsPageTabViewUIColorThemeOptionMenuEventHandler(Theme):
    Oblivion = r"d:\dev\python\Text Gauntlet\Sweetkind.json"
    match Theme:
        case x if x == "Oblivion":
            with open("launch.txt", "w") as f:
                f.write("Oblivion")
            HardRestart()
        case y if y == "Blue":
            with open("launch.txt", "w") as f:
                f.write("blue")
            HardRestart()
        case z if z == "Green":
            with open("launch.txt", "w") as f:
                f.write("green")
            HardRestart()
        case i if i == "Dark Blue":
            with open("launch.txt", "w") as f:
                f.write("dark-blue")
            HardRestart()


def HardRestart():
    python = sys.executable
    os.execl(python, python, *sys.argv)


# --------------------------------------------------------------------------------#


# Displaying a Specific Page to the MainFrame:
def MainFramePageDisplay(Page):
    Page.grid(
        row=0,
        column=0,
        padx=(10, 10),
        pady=(10, 10),
        sticky="nsew",
    )


# Clearing the MainFrame:
def MainFrameGridPagesForget():
    Pages = [
        HomePage,
        ModelPage,
        SongLyricsPage,
        MovieReviewsPage,
        UrlPage,
        SettingsPage,
    ]

    for Page in Pages:
        Page.grid_forget()


# --------------------------------------------------------------------------------#


# Functions Called From Event Handler Functions:
# Setting the Appearance:
def SettingsPageTabViewUIApperanceModeOptionMenuEventHandler(Appearance):
    ctk.set_appearance_mode(Appearance)


# Setting the Scail:
def SettingsPageTabViewUIScalingOptionMenuEventHandler(Scaling):
    ctk.set_widget_scaling(int(Scaling.replace("%", "")) / 100)


# Displaying the Model Output to the Output Table:
def ModelTableOutputDisplayModelOutput(AnalyzedTextDataFrame):
    ModelTableOutput.update_values(
        values=[
            item.insert(0, idx + 1) or item
            for idx, item in enumerate(AnalyzedTextDataFrame.to_numpy().tolist()[:10])
        ]
    )


# Clearing the Output Table:
def ModelClearOutputButtonEventHandler():
    ModelTableOutput.update_values(
        values=[],
    )


def SongLyricsPageTableDisplaySentimentAnalysesDataFrame(
    LyricsSentimentAnalysesDataFrame,
):
    SongLyricsPageSentimentAnalysesOutputTableTable.update_values(
        values=[
            item.insert(0, idx + 1) or item
            for idx, item in enumerate(
                LyricsSentimentAnalysesDataFrame.to_numpy().tolist()[:10]
            )
        ]
    )


def center_window(root, width, height):
    screen_width = 1920
    screen_height = 1080

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    root.geometry(f"{width}x{height}+{x}+{y}")

    
# --------------------------------------------------------------------------------#

# Creating the MainApp:
MainApp = ctk.CTk()
MainApp.title("Text Gauntlet")
MainApp.iconbitmap("assets/icon.ico")
center_window(MainApp, 1000, 450)
# MainApp.geometry("1000x450")
MainApp.resizable(
    height=True,
    width=True,
)
MainApp.grid_rowconfigure(
    0,
    weight=1,
)
MainApp.grid_columnconfigure(
    0,
    weight=0,
)
MainApp.grid_columnconfigure(
    1,
    weight=1,
)


# Creating Gridding and Displaying the Navigation Frame:
NavigationFrame = ctk.CTkFrame(
    master=MainApp,
)
NavigationFrame.grid(
    row=0,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)
NavigationFrame.grid_rowconfigure(
    (0, 1, 2, 3, 4, 5, 6),
    weight=1,
)
NavigationFrame.grid_columnconfigure(
    0,
    weight=0,
)

NavigationFrameLabel = ctk.CTkLabel(
    master=NavigationFrame,
    text="TG",
    font=("Bold", 20),
)
NavigationFrameLabel.grid(
    row=0,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

# Home navigation button:
HomePageNavigationButton = ctk.CTkButton(
    master=NavigationFrame,
    text="Home",
    command=HomePageNavigationButtonEventHandler,
)
HomePageNavigationButton.grid(
    row=1,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)


# Model Navigation Button:
ModelPageNavigationButton = ctk.CTkButton(
    master=NavigationFrame,
    text="Model",
    command=ModelPageNavigationButtonEventHandler,
)
ModelPageNavigationButton.grid(
    row=2,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)


# Song Lyrics Navigation Button:
SonLyricsPageNavigationButton = ctk.CTkButton(
    master=NavigationFrame,
    text="Song Lyrics",
    command=SongLyricsPageNavigationButtonEventHandler,
)
SonLyricsPageNavigationButton.grid(
    row=3,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)


# --------------------------------------------------------------------------------#


# Moview Reviews Navigation Button:
MovieReviewsPageNavigationButton = ctk.CTkButton(
    master=NavigationFrame,
    text="Movie Reviews",
    command=MovieReviewsPageNavigationButtonEventHandler,
)
MovieReviewsPageNavigationButton.grid(
    row=4,
    column=0,
    sticky="nsew",
    padx=(10, 10),
    pady=(10, 10),
)


# --------------------------------------------------------------------------------#


# Url Navigation Button:
UrlPageNavigationButton = ctk.CTkButton(
    master=NavigationFrame,
    text="Article",
    command=UrlPageNavigationButtonEventHandler,
)
UrlPageNavigationButton.grid(
    row=5,
    column=0,
    sticky="nsew",
    padx=(10, 10),
    pady=(10, 10),
)

# Settings Navigation Button:
SettingsPageNavigationButton = ctk.CTkButton(
    master=NavigationFrame,
    text="Settings",
    command=SettingsPageNavigationButtonEventHandler,
)
SettingsPageNavigationButton.grid(
    row=6,
    column=0,
    sticky="nsew",
    padx=(10, 10),
    pady=(10, 10),
)


# Main Frame:
MainFrame = ctk.CTkFrame(
    master=MainApp,
)
MainFrame.grid(
    row=0,
    column=1,
    sticky="nsew",
)
MainFrame.grid_rowconfigure(
    0,
    weight=1,
)
MainFrame.grid_columnconfigure(
    0,
    weight=1,
)


# --------------------------------------------------------------------------------#


# Creating and Gridding the MainFrame:
HomePage = ctk.CTkFrame(MainFrame)
HomePage.grid_rowconfigure(
    0,
    weight=0,
)
HomePage.grid_rowconfigure(
    1,
    weight=1,
)
HomePage.grid_columnconfigure(
    0,
    weight=1,
)

HomePageLabel = ctk.CTkLabel(
    master=HomePage,
    text="Home Page",
    font=("Arial", 24),
)
HomePageLabel.grid(
    row=0,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

HomePageTextBox = ctk.CTkTextbox(
    master=HomePage,
    state="normal",
    wrap="word",
    font=("Bold Italic", 14),
)
HomePageTextBox.grid(
    row=1,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)
HomePageTextBox.insert(
    index=0.0,
    text="""Welcome To Text Gauntlet!
    
Text Gauntlet is an app fully created with Python and Custom Tkinter library.
It is an app with the primary purpose of sentiment analyses, the user can enter any text to get the emotions/sentiment analyses of it.
    
Bonus features include:
    
-A modern graphical user interface with multiple scailing setting, appearances includin but not limited to blue, dark blue, green, and a custom made apearance called Oblivion built using Custom Tkinter Theme Maker (Which is also fully made using tkinter library) and also comes in light and dark mode.
    
-Song Lyrics Sentiment Analyses: the user can enter the name of an artist and a song from that artist and the program will get the lyrics using the Lyrics Genius API and perform sentiment analyses on it and display it to the user.
    
-Movie Reviews Sentiment Analyses: the user can enter the name of any movie and using the IMDb API the program will get the top reviews of said movie and perform sentiment analyses on it and display the output.
    
    Made By: Montaser Amoor & Hisham Qasrawi""",
)
HomePageTextBox.configure(
    state="disabled",
)


# --------------------------------------------------------------------------------#


ModelPage = ctk.CTkFrame(MainFrame)
ModelPage.grid_rowconfigure(
    (0, 1),
    weight=0,
)
ModelPage.grid_rowconfigure(
    (2, 3),
    weight=1,
)
ModelPage.grid_rowconfigure(
    4,
    weight=0,
)
ModelPage.grid_columnconfigure(
    (0, 1),
    weight=1,
)

ModelPageLabel = ctk.CTkLabel(
    master=ModelPage,
    text="Model Page",
    font=("Arial", 24),
)
ModelPageLabel.grid(
    row=0,
    column=0,
    columnspan=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="new",
)

ModelInputTextBoxLabel = ctk.CTkLabel(
    master=ModelPage,
    text="Input Text:",
    font=("Arial", 14),
)
ModelInputTextBoxLabel.grid(
    row=1,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

ModelTextBoxInput = ctk.CTkTextbox(
    master=ModelPage,
    state="normal",
    wrap="word",
)
ModelTextBoxInput.grid(
    row=2,
    rowspan=2,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

ModelPageAnalyzeButton = ctk.CTkButton(
    master=ModelPage,
    text="Analyze",
    command=ModelPageAnalyzeButtonEventHandler,
)
ModelPageAnalyzeButton.grid(
    row=4,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

ModelLabelOutput = ctk.CTkLabel(
    master=ModelPage,
    text="Emotions:",
    font=("Arial", 14),
)
ModelLabelOutput.grid(
    row=1,
    column=1,
    padx=(15, 10),
    pady=(10, 10),
    sticky="nsw",
)

ModelTableOutput = CTkTable(
    master=ModelPage,
    row=10,
    column=3,
    values=[],
    justify="left",
)
ModelTableOutput.grid(
    row=2,
    rowspan=2,
    column=1,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

ModelClearOutputButton = ctk.CTkButton(
    master=ModelPage,
    text="Clear",
    command=ModelClearOutputButtonEventHandler,
)
ModelClearOutputButton.grid(
    row=4,
    column=1,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)


# --------------------------------------------------------------------------------#


SongLyricsPage = ctk.CTkFrame(MainFrame)
SongLyricsPage.grid_rowconfigure(
    0,
    weight=0,
)
SongLyricsPage.grid_rowconfigure(
    (1, 2, 3, 4, 5),
    weight=1,
)
SongLyricsPage.grid_columnconfigure(
    (0, 1, 2, 3),
    weight=1,
)

SongLyricsPageLabel = ctk.CTkLabel(
    master=SongLyricsPage,
    text="Song Lyrics Page",
    font=("Arial", 24),
)
SongLyricsPageLabel.grid(
    row=0,
    column=0,
    columnspan=4,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

SongLyricsPageArtistLabel = ctk.CTkLabel(
    master=SongLyricsPage,
    text="Artist: ",
    font=("Arial", 16),
)
SongLyricsPageArtistLabel.grid(
    row=1,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

SongLyricsPageArtistEntry = ctk.CTkEntry(
    master=SongLyricsPage,
    width=200,
    height=30,
    placeholder_text="Enter Artist Name: ",
    placeholder_text_color="grey",
)
SongLyricsPageArtistEntry.grid(
    row=1,
    column=1,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

SongLyricsPageSongLabel = ctk.CTkLabel(
    master=SongLyricsPage,
    text="Song: ",
    font=("Arial", 16),
)
SongLyricsPageSongLabel.grid(
    row=2,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

SongLyricsPageSongEntry = ctk.CTkEntry(
    master=SongLyricsPage,
    width=200,
    height=30,
    placeholder_text="Enter Song Name: ",
    placeholder_text_color="grey",
)
SongLyricsPageSongEntry.grid(
    row=2,
    column=1,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

SongLyricsPageOutputTextBoxLabel = ctk.CTkLabel(
    master=SongLyricsPage,
    text="Lyrics: ",
    font=("Arial", 16),
)
SongLyricsPageOutputTextBoxLabel.grid(
    row=3,
    column=0,
    columnspan=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

SongLyricsPageOutputTextBox = ctk.CTkTextbox(
    master=SongLyricsPage,
    state="disabled",
    wrap="word",
    font=("Arial", 16),
)
SongLyricsPageOutputTextBox.grid(
    row=4,
    column=0,
    columnspan=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

SongLyricsPageGetLyricsButton = ctk.CTkButton(
    master=SongLyricsPage,
    text="Get Lyrics",
    width=200,
    height=30,
    command=SongLyricsPageGetLyricsButtonEventHandler,
)
SongLyricsPageGetLyricsButton.grid(
    row=5,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

SongLyricsPageAnalyzeLyricsButton = ctk.CTkButton(
    master=SongLyricsPage,
    text="Analyze",
    width=200,
    height=30,
    command=SongLyricsPageAnalyzeLyricsButtonEventHandler,
)
SongLyricsPageAnalyzeLyricsButton.grid(
    row=5,
    column=1,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

SongLyricsPageSentimentAnalysesOutputTableLabel = ctk.CTkLabel(
    master=SongLyricsPage,
    text="Emotions: ",
    font=("Arial", 16),
)
SongLyricsPageSentimentAnalysesOutputTableLabel.grid(
    row=1,
    column=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

SongLyricsPageSentimentAnalysesOutputTableTable = CTkTable(
    master=SongLyricsPage,
    row=10,
    column=3,
    values=[],
    justify="left",
)
SongLyricsPageSentimentAnalysesOutputTableTable.grid(
    row=2,
    column=2,
    rowspan=3,
    columnspan=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

SongLyricsPageSentimentAnalysesOutputTableClearButton = ctk.CTkButton(
    master=SongLyricsPage,
    text="Clear",
    height=30,
    command=SongLyricsPageSentimentAnalysesOutputTableClearButtonEventHandler,
)
SongLyricsPageSentimentAnalysesOutputTableClearButton.grid(
    row=5,
    column=2,
    columnspan=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

# --------------------------------------------------------------------------------#


MovieReviewsPage = ctk.CTkFrame(MainFrame)
MovieReviewsPage.grid_rowconfigure(
    0,
    weight=0,
)
MovieReviewsPage.grid_rowconfigure(
    (1, 2, 3, 4),
    weight=1,
)
MovieReviewsPage.grid_columnconfigure(
    (0, 1, 2, 3),
    weight=1,
)

MovieReviewsPageLabel = ctk.CTkLabel(
    master=MovieReviewsPage,
    text="Movie Reviews Page",
    font=("Arial", 24),
)
MovieReviewsPageLabel.grid(
    row=0,
    column=0,
    columnspan=4,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

MovieReviewsPageMovieLabel = ctk.CTkLabel(
    master=MovieReviewsPage,
    text="Movie:",
    font=("Arial", 16),
)
MovieReviewsPageMovieLabel.grid(
    row=1,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

MovieReviewsPageMovieEntry = ctk.CTkEntry(
    master=MovieReviewsPage,
    width=200,
    height=30,
    placeholder_text="Enter Movie Name: ",
    placeholder_text_color="grey",
)
MovieReviewsPageMovieEntry.grid(
    row=1,
    column=1,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

MovieReviewsPageReviewsLabel = ctk.CTkLabel(
    master=MovieReviewsPage,
    text="Reviews:",
    font=("Arial", 16),
)
MovieReviewsPageReviewsLabel.grid(
    row=2,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

MovieReviewsPageReviesTextBox = ctk.CTkTextbox(
    master=MovieReviewsPage,
    state="disabled",
    wrap="word",
    font=("Arial", 16),
)
MovieReviewsPageReviesTextBox.grid(
    row=3,
    column=0,
    columnspan=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

MovieReviewsPageGetReviewButton = ctk.CTkButton(
    master=MovieReviewsPage,
    text="Get Reviews",
    width=200,
    height=30,
    command=MovieReviewsPageGetReviewButtonEventHandler,
)
MovieReviewsPageGetReviewButton.grid(
    row=4,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

MovieReviewsPageAnalyzeButton = ctk.CTkButton(
    master=MovieReviewsPage,
    text="Analyze",
    width=200,
    height=30,
    command=MovieReviewsPageAnalyzeButtonEventHandler,
)
MovieReviewsPageAnalyzeButton.grid(
    row=4,
    column=1,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

MovieReviewsPageSentimentAnalysesReviewsLabel = ctk.CTkLabel(
    master=MovieReviewsPage,
    text="Emotions:",
    font=("Arial", 16),
)
MovieReviewsPageSentimentAnalysesReviewsLabel.grid(
    row=1,
    column=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsw",
)

MovieReviewsSentimentAnalysesOutputTableTable = CTkTable(
    master=MovieReviewsPage,
    row=10,
    column=3,
    values=[],
    justify="left",
)
MovieReviewsSentimentAnalysesOutputTableTable.grid(
    row=2,
    column=2,
    rowspan=2,
    columnspan=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

MovieReviewsPageSentimentAnalysesTableClearButton = ctk.CTkButton(
    master=MovieReviewsPage,
    text="Clear",
    height=30,
    command=MovieReviewsPageSentimentAnalysesTableClearButtonEventHandler,
)
MovieReviewsPageSentimentAnalysesTableClearButton.grid(
    row=4,
    column=2,
    columnspan=2,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)


# --------------------------------------------------------------------------------#


UrlPage = ctk.CTkFrame(MainFrame)
UrlPage.grid_rowconfigure(
    0,
    weight=1,
)
UrlPage.grid_columnconfigure(0, weight=1)

UrlPageLabel = ctk.CTkLabel(
    master=UrlPage,
    text="Url Page",
    font=("Arial", 24),
)
UrlPageLabel.grid(
    row=0,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)


# --------------------------------------------------------------------------------#


# Creating And Gridding the Settings Page:
SettingsPage = ctk.CTkFrame(MainFrame)
SettingsPage.grid_rowconfigure(
    0,
    weight=0,
)
SettingsPage.grid_rowconfigure(
    1,
    weight=1,
)
SettingsPage.grid_columnconfigure(
    0,
    weight=1,
)

# Creating And Placing The Settings Page Label:
SettingsPageLabel = ctk.CTkLabel(
    master=SettingsPage,
    text="Settings",
    font=("Arial", 24),
)
SettingsPageLabel.grid(
    row=0,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

# Creating And Placing The Settings Page Tab View:
SettingsPageTabView = ctk.CTkTabview(
    master=SettingsPage,
    width=300,
    height=300,
)
SettingsPageTabView.grid(
    row=1,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

# Creating And Placing Tabs:
# Creating The "General" Tab:
# SettingsPageTabView.add(
#     "General",
# )
# SettingsPageTabView.tab("General").grid_rowconfigure(
#     0,
#     weight=1,
# )
# SettingsPageTabView.tab("General").grid_columnconfigure(
#     0,
#     weight=1,
# )

# Creating And Placing The General Tab Label
# SettingsPageTabViewGeneralLabel = ctk.CTkLabel(
#     SettingsPageTabView.tab("General"),
#     text="General Tab",
# )
# SettingsPageTabViewGeneralLabel.grid(
#     row=0,
#     column=0,
#     sticky="nsew",
# )

SettingsPageTabView.add(
    "UI",
)
SettingsPageTabView.tab("UI").grid_rowconfigure(
    (0, 1, 2),
    weight=1,
)
SettingsPageTabView.tab("UI").grid_columnconfigure(
    (0, 1, 2),
    weight=0,
)

SettingsPageTabViewUIAppearanceModeLabel = ctk.CTkLabel(
    SettingsPageTabView.tab("UI"),
    text="Appearence Mode: ",
)
SettingsPageTabViewUIAppearanceModeLabel.grid(
    row=0,
    column=0,
    sticky="nw",
)

SettingsPageTabViewUIAppearanceModeOptionMenu = ctk.CTkOptionMenu(
    master=SettingsPageTabView.tab("UI"),
    values=[
        "System",
        "Light",
        "Dark",
    ],
    command=SettingsPageTabViewUIApperanceModeOptionMenuEventHandler,
)
SettingsPageTabViewUIAppearanceModeOptionMenu.grid(
    row=0,
    column=1,
    sticky="nw",
)


SettingsPageTabViewUIColorThemeOptionMenuLabel = ctk.CTkLabel(
    master=SettingsPageTabView.tab("UI"),
    text="Color Theme: ",
)
SettingsPageTabViewUIColorThemeOptionMenuLabel.grid(
    row=1,
    column=0,
    sticky="nw",
)

SettingsPageTabViewUIColorThemeOptionMenu = ctk.CTkOptionMenu(
    master=SettingsPageTabView.tab("UI"),
    values=[
        "Oblivion",
        "Blue",
        "Green",
        "Dark Blue",
    ],
    command=SettingsPageTabViewUIColorThemeOptionMenuEventHandler,
)
SettingsPageTabViewUIColorThemeOptionMenu.grid(
    row=1,
    column=1,
    sticky="nw",
)


SettingsPageTabViewUIScalingLabel = ctk.CTkLabel(
    master=SettingsPageTabView.tab("UI"),
    text="UI Scaling: ",
)
SettingsPageTabViewUIScalingLabel.grid(
    row=2,
    column=0,
    sticky="nw",
)
SettingsPageTabViewUIScalingOptionMenu = ctk.CTkOptionMenu(
    master=SettingsPageTabView.tab("UI"),
    values=["100%", "90%", "80%", "70%"],
    command=SettingsPageTabViewUIScalingOptionMenuEventHandler,
)
SettingsPageTabViewUIScalingOptionMenu.grid(
    row=2,
    column=1,
    sticky="nw",
)


# --------------------------------------------------------------------------------#


SettingsPageTabView.add(
    "User",
)

SettingsPageTabView.tab("User").grid_rowconfigure(
    0,
    weight=1,
)
SettingsPageTabView.tab("User").grid_columnconfigure(
    0,
    weight=1,
)

SettingsPageTabViewGeneralLabel = ctk.CTkLabel(
    SettingsPageTabView.tab("User"),
    text="User Tab",
)
SettingsPageTabViewGeneralLabel.grid(
    row=0,
    column=0,
    sticky="nsew",
)

SettingsPageTabView.add(
    "App",
)

SettingsPageTabView.tab("App").grid_rowconfigure(
    0,
    weight=1,
)
SettingsPageTabView.tab("App").grid_columnconfigure(
    0,
    weight=1,
)

SettingsPageTabViewRestartAppButton = ctk.CTkButton(
    master=SettingsPageTabView.tab("App"),
    text="RESTART APP",
    fg_color="red",
    hover_color="#A72626",
    command=HardRestart,
)
SettingsPageTabViewRestartAppButton.grid(
    row=0,
    column=0,
    padx=(10, 10),
    pady=(10, 10),
    sticky="nsew",
)

SettingsPageTabView.add(
    "Help",
)

SettingsPageTabView.tab("Help").grid_rowconfigure(
    0,
    weight=1,
)
SettingsPageTabView.tab("Help").grid_columnconfigure(
    0,
    weight=1,
)

SettingsPageTabViewGeneralLabel = ctk.CTkLabel(
    SettingsPageTabView.tab("Help"),
    text="Help Tab",
)
SettingsPageTabViewGeneralLabel.grid(
    row=0,
    column=0,
    sticky="nsew",
)

SettingsPageTabView.add("About")
SettingsPageTabView.tab("About").grid_rowconfigure(
    0,
    weight=1,
)
SettingsPageTabView.tab("About").grid_columnconfigure(
    0,
    weight=1,
)

SettingsPageTabViewGeneralLabel = ctk.CTkLabel(
    SettingsPageTabView.tab("About"),
    text="About Tab",
)
SettingsPageTabViewGeneralLabel.grid(
    row=0,
    column=0,
    sticky="nsew",
)


# --------------------------------------------------------------------------------#


def main():
    global Model
    Model = WakeUpRoBERTa()
    MainFramePageDisplay(HomePage)
    MainApp.mainloop()


if __name__ == "__main__":
    main()
