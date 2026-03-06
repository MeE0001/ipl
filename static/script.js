function search(){

    let country=document.getElementById("search").value
    
    fetch("/search?country="+country)
    .then(res=>res.json())
    .then(data=>{
    
    let div=document.getElementById("players")
    
    div.innerHTML=""
    
    data.forEach(p=>{
    
    div.innerHTML+=`
    <div>
    
    <h3>${p.name}</h3>
    
    Country: ${p.country}<br>
    Role: ${p.role}<br>
    Current Bid: ${p.current_bid}
    
    <br><br>
    
    <a href="/player/${p.player_id}">Join Auction</a>
    
    </div><hr>
    `
    
    })
    
    })
    
    }