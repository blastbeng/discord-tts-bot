'use strict';
const Core = require('../../Core.js');

async function routes(fastify, options) {

    fastify.get('/', async (request, reply) => {
        return { msg: 'Management' };
    });

    fastify.get('/clear', async (request, reply) => {
        return { test: 1 };
    });

    fastify.get('/scrape', async (request, reply) => {
        const scraperType = request.query.scraper;
        //const pageNum = request.query.pageNum !== undefined ? request.query.pageNum : 1;
        let pageNum = 1;
        if (request.query.pageNum !== undefined) {
            pageNum = request.query.pageNum;
        } else {
            let max = 100;
            let min = 0;
            let difference = max - min;
            let rand = Math.random();
            rand = Math.floor(rand * difference);
            rand = rand + min;
            pageNum = rand;
        }
        let number = 0;
        if (scraperType && (false !== (scraperType in Core.SERVICE))) {
            number = await Core.scrape(scraperType, pageNum);
        } else {
            let scrapers = undefined;
            for (const key of Object.keys(Core.SERVICE)) {
                scrapers = (scrapers !== undefined ? scrapers + ", " : "") + key;
            }
            throw new Error("Please provide a valid services. (" + scrapers + ")");
        }
        //else {
        //    for (const key of Object.keys(Core.SERVICE)) {
        //        number = await Core.scrape(key, pageNum);
        //    }
        //}
        number.scraper = scraperType;
        return { status: 'OK', ...number };
    });
}

module.exports = routes;