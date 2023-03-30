# The Jaundice News filter

So far, only one news site is supported - [ИНОСМИ.РУ](https://inosmi.ru/). A special adapter has been developed for it, which is able to highlight the text of the article against the background of the rest of the HTML markup. Other news sites will require new adapters, all of them will be located in the `adapters` directory. The code for the INOSMI website is also placed there.RU: `jaundice_rate/adapters/inosmi_ru.py `.

# How to install

You need:
* Python >= 3.10
* [Poetry](https://python-poetry.org/docs/)

Run commands:
```bash
make install
make env
```

# How to run

To start the server, run the command and go to http://0.0.0.0:8080?urls={urls}

`urls` - urls of articles from the inosmi website:
```bash
make server
```

---

To run the cli utility, add links to articles in `jaundice_rate/settings.py` `TEST_JAUNDICE_ARTICLE_URLS` and run the command:
```bash
make run
```


# How to test

```bash
make test
```
