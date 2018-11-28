import React, { Component } from 'react';
import './header.css';
import FileUploadProgress  from 'react-fileupload-progress';
//https://www.npmjs.com/package/react-fileupload-progress
import {getURL, getData} from './urls';
import ConfigNewStuff from './configStuff';
import ConfigHier from './hier';
// import ConfigWeights from './configWeights';

class Header extends Component {
    constructor(props){
        super(props);
        this.state={showPicker:false,tables:undefined,id:undefined,avStuff:undefined,hiers:undefined}
    }

    render(){
        return(
            <div key='header' className="App-header">
                {/* <ConfigWeights key='configW'/> */}
                
                <button key='AddFile' className="button" 
                    onClick={(e) => {this.setState({showPicker:!this.state.showPicker,
                                                    id:undefined,
                                                    tables:undefined});}}> 
                    Upload file
                </button> 
                {this.state.showPicker?
                    <FileUploadProgress key='fup' url={getURL.Upload()}
                        // onProgress={(e, request, progress) => {
                        //     console.log('progress', e, request, progress);
                        // }}
                        onLoad={ (e, request) => {
                            let data=JSON.parse(e.target.response);
                            let errorList='';
                            for (let v in data.status){
                                if (parseInt(data.status[v],10)===-1){
                                    if (errorList!==''){
                                        errorList=errorList+','
                                    }
                                    errorList=errorList+' '+v;
                                }
                            }
                            if (errorList!==''){
                                alert('The following files could not be imported: '+errorList);
                            }else{
                                this.setState({showPicker:false,id:data.id});                            
                            }
                            getData(getURL.TemporaryTables(data.id),(TT)=>{
                                this.setState({tables:TT});
                            })
                            
                        }}
                        onError={ (e, request) => {console.log('error', e, request);}}
                        onAbort={ (e, request) => {console.log('abort', e, request);}}
                    />
                :null}
                <button 
                    key='CreateHier' 
                    className="button" 
                    onClick={(e) => {
                        if (this.state.avStuff!==undefined){
                            this.setState({avStuff:undefined,tables:undefined});
                        }else{
                            getData(getURL.AvailableVarsnGeo(),(ret)=>{
                                console.log(ret);
                                this.setState({avStuff:ret,tables:undefined});
                            })    
                        }
                    }}
                    > 
                    Create hierarchy
                </button> 
                {this.state.tables!==undefined? <ConfigNewStuff key='configstuff' data={this.state.tables}/>:null}
                {this.state.avStuff!==undefined? <ConfigHier key='configHier' data={this.state.avStuff}/>:null}
            </div>
        );
    }
}

export default Header;
