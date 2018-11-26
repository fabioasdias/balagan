import React, { Component } from 'react';
import './hier.css';
import { sendData, getURL } from './urls';

class ConfigHier extends Component {
    constructor(props){
        super(props);
        this.state={selVar:undefined}
    }

    render(){
        let vars=this.props.data.variables;
        return(
            <div className='OneLine'> 
                Variable: 
                <select 
                    className="dropboxes" 
                    onChange={(e)=>{
                        this.setState({selVar:e.target.value});
                    }} 
                    >
                    <option 
                        disabled 
                        selected={this.state.selVar===undefined} 
                        value=''>
                    </option>
                    {vars.map( (e) => {
                        return(<option 
                                    value={e.VarID} 
                                    key={e.VarID}
                                    selected={e.VarID===this.state.selVar}
                                > 
                                {e.name+' - "'+e.sample+'" - '+e.desc} 
                                </option>)
                    })}
                </select>
                <button 
                    key='GoHier' 
                    className="button" 
                    onClick={(e) => {
                        sendData(getURL.CreateHierarchy(),{VarID:this.state.selVar},(ret)=>{
                            console.log(ret);
                            // this.setState({avStuff:ret});
                        })
                    }}
                    > 
                    OK
                </button> 
                
            </div>);
    }
}
export default ConfigHier;
