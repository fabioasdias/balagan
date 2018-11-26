import React, { Component } from 'react';
import './hier.css';
import { connect } from 'react-redux';
import { sendData, getURL, getData } from './urls';
import { actionCreators } from './reducers';

const mapStateToProps = (state) => ({
    hiers: state.hiers,
    detailLevel: state.detailLevel,
  });


class ConfigWeights extends Component {
    constructor(props){
        super(props);
        this.state={hiers:undefined};
    }

    componentDidMount(){
        getData(getURL.AvailableHiers(),(ret)=>{
            this.setState({hiers:ret});        
        })
    }

    render(){
        console.log(this.props);
        if ((this.state.hiers===undefined)||(this.state.hiers.length===0)){
            return(null);
        }
        let retJSX=[];
        
        let {dispatch}=this.props;
        let wChange=(e)=>{
            let K=parseInt(e.target.getAttribute('data-i'),10);
            let cH=this.state.hiers.slice();
            cH[K].auto=false;                        
            let N=0;
            let S=0;
            for (let i=0; i< cH.length;i++){
                if (cH[i].auto){
                    N=N+1;
                }
                else{
                    if (i!==K){
                        S=S+cH[i].w;
                    }
                }
            }
            
            let cW=e.target.value/100;
            cH[K].w=(S+cW>1)?1-S:cW;

            S=S+cH[K].w;
            let nW=(1-S)/N;
            for (let i=0; i < cH.length;i++){
                if ((i!==K)&&(cH[i].auto)){
                    cH[i].w=nW;
                }
            }  
            this.setState({hiers:cH});
            
        }

        let det=this.props.detailLevel;

        retJSX.push(<div>
                        <p style={{width:'fit-content',margin:'auto',marginTop:'20px'}}>Level of detail</p>

                        <div className="OneLine" style={{margin:'auto',width:'fit-content'}}>
                            Less
                            <input 
                                type="range" 
                                className="slider" 
                                key={'HierCut'}
                                min={0} 
                                max={100} 
                                value={Math.round(100*(1-det))} 
                                onChange={(e)=>{dispatch(actionCreators.UpdateDetailLevel(1-e.target.value/100));}}
                            />More
                        </div>
                    </div>)


        retJSX.push(<p style={{width:'fit-content',margin:'auto',marginTop:'20px'}}>Weights</p>)
        let {hiers}=this.state;
        for (let i=0;i<hiers.length;i++){
            let h=hiers[i];
            retJSX.push(<div
                            className="OneLine">
                            <p style={{width:'100px'}}>{h.name}</p>
                            <input 
                                type="range" 
                                className="slider" 
                                key={'sl'+h.HierID}
                                data-i={i}
                                min={0} 
                                max={100} 
                                value={Math.round(100*(+h.w))} 
                                onChange={wChange}
                            /><p style={{width:'50px'}}>{Math.round(100*(h.w))}%</p></div>)
        }
        retJSX.push(
            <button key='AddFile' className="button" 
                onClick={(e) => {dispatch(actionCreators.UpdateWeights(this.state.hiers));}}> 
                Update
            </button> );
        return(<div className="WeightBlock">{retJSX}</div>);
    }
}
export default connect(mapStateToProps)(ConfigWeights);
    