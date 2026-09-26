const API="https://openlibrary.org";
const AI_API="http://127.0.0.1:5000";

let currentBook=null;
let heroBooks=[];
let heroIndex=0;

const $=id=>document.getElementById(id);

const modal=$("bookModal");
const modalCover=$("modalCover");
const modalTitle=$("modalTitle");
const modalAuthor=$("modalAuthor");
const modalYear=$("modalYear");
const modalDescription=$("modalDescription");
const recommendButton=$("recommendButton");
const recommendationSection=$("recommendationSection");
const recommendationRow=$("recommendationRow");
const searchInput=$("searchInput");
const searchButton=$("searchButton");
const searchSection=$("searchSection");
const searchGrid=$("searchResults");

// =========================================================
// HELPERS
// =========================================================

function escapeHTML(text){
    const div=document.createElement("div");
    div.textContent=text??"";
    return div.innerHTML;
}

function getCover(id,size="M"){
    return id
        ?`https://covers.openlibrary.org/b/id/${id}-${size}.jpg`
        :"";
}

function formatSearchBook(book){
    return{
        Title:book.title||"Unknown title",
        Author:book.author_name?.[0]||"Unknown author",
        Year:book.first_publish_year||"Unknown year",
        "Work ID":book.key||"",
        Cover:getCover(book.cover_i)
    };
}

function formatSubjectBook(book){
    return{
        Title:book.title||"Unknown title",
        Author:book.authors?.[0]?.name||"Unknown author",
        Year:book.first_publish_year||"Unknown year",
        "Work ID":book.key||"",
        Cover:getCover(book.cover_id)
    };
}

// =========================================================
// OPEN LIBRARY API
// =========================================================

async function getSubjectBooks(subject,limit=12){

    const controller=new AbortController();

    const timeout=setTimeout(
        ()=>controller.abort(),
        10000
    );

    try{

        const response=await fetch(
            `${API}/subjects/${encodeURIComponent(subject)}.json?limit=${limit}`,
            {signal:controller.signal}
        );

        clearTimeout(timeout);

        if(!response.ok)
            throw new Error(`HTTP ${response.status}`);

        const data=await response.json();

        console.log(
            `${subject}:`,
            data.works?.length||0,
            "books"
        );

        return data.works||[];

    }catch(error){

        clearTimeout(timeout);

        console.error(
            `Error loading ${subject}:`,
            error
        );

        return[];
    }
}

async function getWorkDetails(workKey){

    if(!workKey)return null;

    try{

        const response=await fetch(
            `${API}${workKey}.json`
        );

        if(!response.ok)
            throw new Error(`HTTP ${response.status}`);

        return await response.json();

    }catch(error){

        console.error(
            "Details error:",
            error
        );

        return null;
    }
}

function getDescription(data){

    if(!data)return"";

    let description=data.description||"";

    if(typeof description==="object")
        description=description.value||"";

    return description;
}

// =========================================================
// BOOK CARD
// =========================================================

function createBookCard(book,searched=false){

    const card=document.createElement("div");

    card.className="book-card";

    card.innerHTML=`
        <div class="book-cover-wrapper">
            <img
                class="book-cover"
                src="${
                    book.Cover||
                    "https://via.placeholder.com/160x240?text=No+Cover"
                }"
                alt="${escapeHTML(book.Title)}"
                loading="lazy"
            >
        </div>

        <div class="book-info">
            <h3>${escapeHTML(book.Title)}</h3>
            <p>${escapeHTML(book.Author)}</p>
        </div>
    `;

    card.addEventListener(
        "click",
        ()=>openBook(book,searched)
    );

    return card;
}

// =========================================================
// CATEGORY ROW
// =========================================================

async function loadCategory(subject,rowId){

    const row=$(rowId);

    if(!row){

        console.error(
            "Missing element:",
            rowId
        );

        return;
    }

    try{

        const books=
            await getSubjectBooks(subject,12);

        row.innerHTML="";

        if(!books.length){

            row.innerHTML=`
                <p class="empty-message">
                    No books available.
                </p>
            `;

            return;
        }

        books.forEach(book=>{

            row.appendChild(
                createBookCard(
                    formatSubjectBook(book),
                    false
                )
            );

        });

    }catch(error){

        console.error(
            subject,
            error
        );

        row.innerHTML=`
            <p class="error-message">
                Could not load books.
            </p>
        `;
    }
}

// =========================================================
// LOAD ALL CATEGORIES
// =========================================================

async function loadHomepage(){

    const categories=[

        ["fiction","popularRow"],
        ["fantasy","fantasyRow"],
        ["science_fiction","scienceRow"],
        ["mystery","mysteryRow"],
        ["romance","romanceRow"],
        ["history","historyRow"],
        ["philosophy","philosophyRow"],
        ["adventure","adventureRow"]

    ];

    await Promise.all(

        categories.map(
            ([subject,rowId])=>
                loadCategory(
                    subject,
                    rowId
                )
        )

    );

    console.log(
        "Homepage categories loaded."
    );
}

// =========================================================
// HERO
// =========================================================

async function loadHero(){

    const books=
        await getSubjectBooks(
            "fiction",
            8
        );

    heroBooks=
        books
            .map(formatSubjectBook)
            .filter(book=>book.Cover);

    showHero();
}

function showHero(){

    if(!heroBooks.length)return;

    const book=
        heroBooks[heroIndex];

    const hero=
        document.querySelector(".hero");

    if(hero){

        hero.style.backgroundImage=
            `url("${book.Cover}")`;

    }

    if($("heroTitle"))
        $("heroTitle").textContent=
            book.Title;

    if($("heroAuthor"))
        $("heroAuthor").textContent=
            `by ${book.Author}`;
}

function nextHero(){

    if(!heroBooks.length)return;

    heroIndex=
        (heroIndex+1)%
        heroBooks.length;

    showHero();
}

function previousHero(){

    if(!heroBooks.length)return;

    heroIndex=
        (heroIndex-1+heroBooks.length)%
        heroBooks.length;

    showHero();
}

$("heroNext")?.addEventListener(
    "click",
    nextHero
);

$("heroPrevious")?.addEventListener(
    "click",
    previousHero
);

setInterval(
    nextHero,
    6000
);

// =========================================================
// SEARCH
// =========================================================

async function searchBooks(query){

    if(!query.trim()){
        return [];
    }

    try{

        const response = await fetch(
            `${API}/search.json?` +
            `q=${encodeURIComponent(query)}` +
            `&limit=30` +
            `&fields=key,title,author_name,first_publish_year,cover_i`
        );

        if(!response.ok){
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        return data.docs || [];

    }catch(error){

        console.error("Search error:", error);

        return [];
    }
}

async function performSearch(){

    const query=
        searchInput?.value.trim();

    if(!query)return;

    searchSection?.classList.remove(
        "hidden"
    );

    if(searchGrid){

        searchGrid.innerHTML=`
            <div class="loading">
                Searching Open Library...
            </div>
        `;
    }

    const books=
        await searchBooks(query);

    if(!searchGrid)return;

    searchGrid.innerHTML="";

    if(!books.length){

        searchGrid.innerHTML=`
            <p class="empty-message">
                No books found.
            </p>
        `;

        return;
    }

    books.forEach(book=>{

        searchGrid.appendChild(
            createBookCard(
                formatSearchBook(book),
                true
            )
        );

    });

    searchSection?.scrollIntoView({
        behavior:"smooth",
        block:"start"
    });
}

searchButton?.addEventListener(
    "click",
    performSearch
);

searchInput?.addEventListener(
    "keydown",
    event=>{

        if(event.key==="Enter")
            performSearch();

    }
);

// =========================================================
// BOOK MODAL
// =========================================================

async function openBook(
    book,
    searched=false
){

    currentBook=book;

    if(modalCover){

        modalCover.src=
            book.Cover||
            "https://via.placeholder.com/300x450?text=No+Cover";

        modalCover.alt=
            book.Title;
    }

    if(modalTitle)
        modalTitle.textContent=
            book.Title;

    if(modalAuthor)
        modalAuthor.textContent=
            `by ${book.Author}`;

    if(modalYear){

        modalYear.textContent=
            book.Year&&
            book.Year!=="Unknown year"
                ?`First published: ${book.Year}`
                :"";
    }

    if(modalDescription)
        modalDescription.textContent=
            "Loading description...";

    // AI button ONLY for search results
    if(recommendButton){

        recommendButton.classList.toggle(
            "hidden",
            !searched
        );
    }

    recommendationSection?.classList.add(
        "hidden"
    );

    if(recommendationRow)
        recommendationRow.innerHTML="";

    modal?.classList.remove(
        "hidden"
    );

    document.body.classList.add(
        "modal-open"
    );

    const workData=
        await getWorkDetails(
            book["Work ID"]
        );

    const description=
        getDescription(workData);

    if(modalDescription){

        modalDescription.textContent=
            description||
            "No description is available for this book.";
    }
}

// =========================================================
// CLOSE MODAL
// =========================================================

function closeModal(){

    modal?.classList.add(
        "hidden"
    );

    document.body.classList.remove(
        "modal-open"
    );

    currentBook=null;
}

$("modalClose")?.addEventListener(
    "click",
    closeModal
);

$("modalBackdrop")?.addEventListener(
    "click",
    closeModal
);

document.addEventListener(
    "keydown",
    event=>{

        if(
            event.key==="Escape"&&
            !modal?.classList.contains("hidden")
        ){

            closeModal();
        }
    }
);

// =========================================================
// TF-IDF AI RECOMMENDATIONS
// =========================================================

async function getAIRecommendations(){

    if(!currentBook)
        return;

    recommendationSection?.classList.remove(
        "hidden"
    );

    if(recommendationRow){

        recommendationRow.innerHTML=`
            <div class="loading">
                <div class="loader"></div>
                <p>
                    AI is finding similar books...
                </p>
            </div>
        `;
    }

    const payload={

        title:
            currentBook.Title,

        author:
            currentBook.Author,

        work_key:
            currentBook["Work ID"]

    };

    console.log(
        "Sending to TF-IDF API:",
        payload
    );

    try{

        const response=
            await fetch(
                `${AI_API}/recommend`,
                {
                    method:"POST",

                    headers:{
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );

        const data=
            await response.json();

        if(!response.ok){

            throw new Error(
                data.error||
                "Recommendation failed."
            );
        }

        const books=
            data.recommendations||[];

        if(!recommendationRow)
            return;

        recommendationRow.innerHTML="";

        if(!books.length){

            recommendationRow.innerHTML=`
                <p class="empty-message">
                    No similar books were found.
                </p>
            `;

            return;
        }

        books.forEach(book=>{

            const formattedBook={

                Title:
                    book.Title||
                    "Unknown title",

                Author:
                    book.Author||
                    "Unknown author",

                Year:
                    book.Year||
                    "Unknown year",

                Cover:
                    book.Cover||
                    "",

                "Work ID":
                    book["Work ID"]||
                    ""

            };

            recommendationRow.appendChild(

                createBookCard(
                    formattedBook,
                    false
                )

            );

        });

    }catch(error){

        console.error(
            "AI API error:",
            error
        );

        if(recommendationRow){

            recommendationRow.innerHTML=`
                <div class="error-message">
                    <p>
                        Could not connect to the AI engine.
                    </p>

                    <small>
                        Make sure
                        <b>python api.py</b>
                        is running.
                    </small>
                </div>
            `;
        }
    }
}

recommendButton?.addEventListener(
    "click",
    getAIRecommendations
);

// =========================================================
// START
// =========================================================

async function initialize(){

    console.log(
        "BookVerse starting..."
    );

    // Both run independently
    loadHero();
    loadHomepage();

    console.log(
        "BookVerse initialized."
    );
}

initialize();