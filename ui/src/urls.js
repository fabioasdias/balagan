const baseURL=()=>{
    // return('http://142.1.190.38:8000/');
    return('http://localhost:8000/');
    //return('http://138.197.139.94/bal/');//alpha
    //return('http://142.1.190.14/bal/')
}

export const requestType ={
    UPLOAD : 'Upload',
    TEMP_TABLES : 'TemporaryTables',
    MOVE_TEMP : 'MoveTemporary',
    AV_VG : 'AvailableVG',
    CREATE_HIER : 'CreateHierarchy',
    MIX_HIER : 'MixHierarchies',
    AV_HIER : 'AvailableHiers',
};

export const getURL  = {
    Upload: () => {
        return(baseURL()+'upload');
    },
    TemporaryTables: (uuid) => {
        let url=baseURL()+'getTemporaryTables';
        if (uuid!==undefined){
            url=url+'?uuid='+uuid;
        }
        return(url);
    },
    AvailableVarsnGeo: () =>{
        return(baseURL()+'getAvailableVG');
    },
    MoveTemporary: () => {
        return(baseURL()+'moveTemp');
    },
    CreateHierarchy: () =>{
        return(baseURL()+'createHierarchy');
    },
    MixHierarchies: () =>{
        return(baseURL()+'mixHierarchies');
    },
    AvailableHiers: () =>{
        return(baseURL()+'getAvailableHiers');
    },
    SimplifiedGeojson: () =>{
        return(baseURL()+'SimplifiedGeojson');
    }

};

export const getData = (url,actionThen) => {
    fetch(url)
    .then((response) => {
      if (response.status >= 400) {throw new Error("Bad response from server");}
      return response.json();
    })
    .then(actionThen);
}

export const sendData=(url,data,callBackFcn)=>{
    fetch(url, {
        body: JSON.stringify(data), // must match 'Content-Type' header
        cache: 'no-cache', // *default, cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *omit
        headers: {
        'user-agent': 'Mozilla/4.0 MDN Example',
        'content-type': 'application/json'
        },
        method: 'POST', // *GET, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *same-origin
        redirect: 'follow', // *manual, error
        referrer: 'no-referrer', // *client
      }).then(
        ret => {
            ret.json().then((d)=> {//promise of a promise. really.
                callBackFcn(d);
            })
            
        },
        error => console.log('Error in fetching post')
    );
}
