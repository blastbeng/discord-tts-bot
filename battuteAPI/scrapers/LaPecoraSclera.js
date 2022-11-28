'use strict';

const cheerio = require('cheerio');
const Scraper = require('./Scraper.js');

/**
 * @class LaPecoraSclera
 * @extends Scraper
 */
class LaPecoraSclera extends Scraper {

    get BASE_URL() {
        return "https://www.lapecorasclera.it/";
    }

    get PAGES() {
        return [{
            page: 'chuck-norris-facts.php?PA={{PAGE}}',
            categories: [Scraper.CATEGORIES.CHUCK_NORRIS]
        }, {
            page: 'battute-divertenti.php?PA={{PAGE}}',
            categories: [Scraper.CATEGORIES.FREDDURE]
        }, {
            page: 'battute-divertenti.php?PA={{PAGE}}&genere=1',
            categories: [Scraper.CATEGORIES.COLMI]
        }, {
            page: 'battute-divertenti.php?PA={{PAGE}}&genere=3',
            categories: [Scraper.CATEGORIES.DIFFERENZE]
        }, {
            page: 'battute-divertenti.php?PA={{PAGE}}&genere=2',
            categories: [Scraper.CATEGORIES.COMESICHIAMA]
        }, {
            page: 'battute-divertenti.php?PA={{PAGE}}&genere=4',
            categories: [Scraper.CATEGORIES.IPERCHE]
        }, {
            page: 'battute-divertenti.php?PA={{PAGE}}&genere=5',
            categories: [Scraper.CATEGORIES.MASSIME]
        }];
    }

    async getJokesFromPage(page, options) {
        const html = await this._downloadPage(page, options);
        const $ = cheerio.load(html);
        const divs = $('.panel-body > div')
        if (!divs) throw new Error("No joke found");
        const jokes = Array.from(divs)
            .map(div => div.children[0].data)
            .map(joke => ({
                text: joke,
                categories: [...page.categories],
                source: 'LaPecoraSclera'
            }));
        return jokes;
    }

}

module.exports = LaPecoraSclera;