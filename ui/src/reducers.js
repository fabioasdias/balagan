export const types={
    UPDATE_WEIGHTS : 'UpdateWeights',
    UPDATE_DETAIL_LEVEL : 'UpdateDetailLevel',
};
// Helper functions to dispatch actions, optionally with payloads
export const actionCreators = {
    UpdateWeights: conf =>{
        return {type: types.UPDATE_WEIGHTS, payload: conf};
    },
    UpdateDetailLevel: level =>{
        return({type: types.UPDATE_DETAIL_LEVEL, payload: level});
    }

  };
export const reducer = (state={hiers:[],detailLevel:0.5}, action)=>{
    const { type, payload } = action;
    console.log(state);
    // console.log(payload);
    switch (type){
        case types.UPDATE_WEIGHTS:
            return({...state, hiers:payload});
        case types.UPDATE_DETAIL_LEVEL:
            return({...state, detailLevel:payload});
        default:
            return(state);
    }
}

