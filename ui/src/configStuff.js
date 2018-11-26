import React, { Component } from 'react';
import './configStuff.css';
//https://www.npmjs.com/package/react-fileupload-progress
import {getURL, sendData} from './urls'

class ConfigGeom extends Component {
    render() {
        let {geom,ids,othergeometries,index,fname}=this.props;
        let {changeCallback}=this.props;
        return(<div className='configGeom'>
                <div className='OneLine'> 
                    <input 
                        className="checkboxes"
                        type="checkbox"
                        checked={geom.enabled}
                        onChange={changeCallback} 
                        data-fname={fname}
                        data-which='enabled'
                        data-field={geom.field}
                        data-index={index}
                        data-kind='geo'
                    />            
                    Geometry name: 
                    <input 
                        className="textBox"
                        defaultValue={geom.name}
                        onBlur={changeCallback} 
                        data-which='name'
                        data-fname={fname}
                        data-field={geom.field}
                        data-index={index}
                        data-kind='geo'
                    /> 
                </div>

                <div className='OneLine'> 
                    Description: 
                    <input 
                        className="textBox"
                        defaultValue={geom.description}
                        onBlur={changeCallback} 
                        data-fname={fname}
                        data-which='description'
                        data-field={geom.field}                        
                        data-index={index}
                        data-kind='geo'
                    />
                </div>

                <div className='OneLine'> 
                    Identifier field: 
                    <select 
                        className="dropboxes" 
                        data-field={geom.field}
                        data-index={index}
                        data-fname={fname}
                        data-which='indexField'
                        data-kind='geo'
                        onChange={changeCallback} 
                        >
                        <option 
                            disabled 
                            selected={geom.indexField===''} 
                            value=''>
                        </option>
                        {ids.map( (e) => {
                            return(<option 
                                        value={e.field} 
                                        key={e.fileContents+e.field}
                                        selected={e.field===geom.indexField}
                                    > 
                                    {e.field+' - "'+e.sample+'"'} 
                                    </option>)
                        })}
                    </select>
                </div>
                {othergeometries.length>0?
                    <div className='OneLine'> Merge with: 
                    <select 
                        className="dropboxes" 
                        data-field={geom.field}
                        data-kind='geo'
                        data-index={index}
                        data-fname={fname}
                        data-which='mergeWith'
                        onChange={changeCallback} 
                    >
                        <option 
                            disabled 
                            selected={''===geom.mergeWith} 
                            value=''>
                        </option>
                        {othergeometries.map( (e) => {
                            return(<option 
                                        value={e.GeoID} 
                                        key={e.GeoID}
                                        selected={e.GeoID===geom.mergeWith}
                                    > 
                                    {e.name} 
                                    </option>)
                        })}
                    </select>
                    </div>:null}
                
               </div>);
    }
}

class ConfigVar extends Component {
    render(){
        let {variable,ids,othervariables,index,fname,useableGeoms}=this.props;
        let {changeCallback}=this.props;        
        return(<div className='configGeom'>
                <div className='OneLine'> 
                    <input 
                        className="checkboxes"
                        type="checkbox"
                        checked={variable.enabled}
                        onChange={changeCallback} 
                        data-index={index}
                        data-fname={fname}
                        data-kind='var'
                        data-which='enabled'
                        data-field={variable.field}
                    />            
                    Variable name: 
                    <input 
                        className="textBox"
                        defaultValue={variable.name}
                        onBlur={changeCallback} 
                        data-index={index}
                        data-fname={fname}
                        data-which='name'
                        data-kind='var'
                        data-field={variable.field}                        
                    /> 
                </div>
                <div className='OneLine'>
                    Sample: 
                    <input
                        readOnly 
                        className="textBox"
                        defaultValue={variable.sample}
                    /> 

                </div>
                <div className='OneLine'> 
                    Description: 
                    <input 
                        className="textBox"
                        defaultValue={variable.description}
                        onBlur={changeCallback} 
                        data-index={index}
                        data-fname={fname}
                        data-kind='var'
                        data-which='description'
                        data-field={variable.field}                        
                    />
                </div>
                <div className='OneLine'> 
                    Identifier field: 
                    <select 
                        className="dropboxes" 
                        data-field={variable.field}
                        data-index={index}
                        data-fname={fname}
                        data-kind='var'
                        data-which='indexField'
                        onChange={changeCallback}                         
                    >
                        <option 
                            disabled 
                            selected={variable.indexField===''} 
                            value='' 
                            >
                        </option>
                        {ids.filter((e)=>{
                                return(e.field!==variable.field);
                            }).map( (e) => {
                            return(<option 
                                        value={e.field} 
                                        key={e.fileContents+e.field}
                                        selected={e.field===variable.indexField}
                                    > 
                                    {e.field+' - "'+e.sample+'"'} 
                                    </option>)
                        })}
                    </select>                    
                </div>
                <div className='OneLine'> 
                    Corresponding geometry: 
                    <select 
                        className="dropboxes" 
                        data-field={variable.field}
                        data-index={index}
                        data-fname={fname}
                        data-kind='var'
                        data-which='useGeom'
                        onChange={changeCallback}                         
                    >
                        <option 
                            disabled 
                            selected={(variable.useGeom==='')}
                            value='' 
                            >
                        </option>
                        {useableGeoms.filter((e)=>{
                                return(e.name!==variable.field);
                            }).map( (e) => {
                            return(<option 
                                        value={e.ind} 
                                        key={e.fileContents+'g'+e.name}
                                        selected={(variable.useGeom===e.ind)}
                                    > 
                                    {e.name} 
                                    </option>)
                        })}
                    </select>
                </div>
{/*                 
                {othervariables.length>0?
                    <div className='OneLine'> Merge with: 
                    <select 
                        className="dropboxes" 
                        data-index={index}
                        data-field={variable.field}
                        data-fname={fname}
                        data-kind='var'
                        data-which='mergeWith'
                        onChange={changeCallback}                         
                    >
                        <option 
                            disabled 
                            selected={variable.mergeWith===''}
                            value=''>
                        </option>
                        {othervariables.map( (e) => {
                            return(<option 
                                        value={e.name} 
                                        key={e.VarID}
                                        selected={e.name===variable.mergeWith}
                                    > 
                                    {e.name} 
                                    </option>)
                        })}
                    </select>
                    </div>:null}                 */}

                    {othervariables.length>0?
                    <div className='OneLine'> Normalize by: 
                    <select 
                        className="dropboxes" 
                        data-index={index}
                        data-field={variable.field}
                        data-fname={fname}
                        data-kind='var'
                        data-which='normalizedBy'
                        onChange={changeCallback}                         
                    >
                        <option 
                            disabled 
                            selected={variable.normalizedBy===''}
                            value=''>
                        </option>
                        {othervariables.map( (e) => {
                            return(<option 
                                        value={e.VarID} 
                                        key={e.VarID}
                                        selected={e.name===variable.normalizedBy}
                                    > 
                                    {e.name} 
                                    </option>)
                        })}
                    </select>
                    </div>:null}                
                    
               </div>);
    }
}

class ConfigNewStuff extends Component {
    constructor(props){
        super(props);
        this.state={id:undefined,newFiles:undefined}
    }
    componentDidMount() {
        let {data}=this.props;
        this.setState({id:data.uuid,newFiles:data.new});    
    }
    
    componentWillUpdate(nextProps) { //TODO  maybe don't need it?
        let {data}=nextProps;
        if (this.state.id!==data.uuid){
            this.setState({id:data.uuid,newFiles:data.new});    
        }
    }
    render(){
        let retJSX=[];
        let getFields=(e)=>{
            let ret={}
            ret.fname=e.target.getAttribute('data-fname');
            ret.field=e.target.getAttribute('data-field');
            ret.which=e.target.getAttribute('data-which');
            ret.index=e.target.getAttribute('data-index');
            ret.kind=e.target.getAttribute('data-kind');
            return(ret);
        }

        let setIndexField=(A,indexField)=>{
            for (let i=0;i<A.length;i++){
                if (A[i].field===indexField){
                    A[i].enabled=false;
                    A[i].indexField=''
                }else{
                    if (A[i].indexField===''){
                        A[i].indexField=indexField;
                    }
                }
            }
            return(A);
        }


        let chgCall= (e)=>{ 
            let f=getFields(e);
            let {geometries,variables}=this.state.newFiles[f.fname];
            switch (f.which){
                case 'indexField':
                    geometries=setIndexField(geometries,e.target.value);
                    variables=setIndexField(variables,e.target.value);
                    break;
                case 'enabled':
                    if (f.kind==='geo'){
                        geometries[f.index]['enabled']=!geometries[f.index]['enabled']
                    }
                    if (f.kind==='var'){
                        variables[f.index]['enabled']=!variables[f.index]['enabled'] 
                    }
                    break;
                default:
                    if (f.kind==='geo'){
                        geometries[f.index][f.which]=e.target.value;
                    }
                    if (f.kind==='var'){
                        variables[f.index][f.which]=e.target.value;
                    }
            }
            let curState=this.state.newFiles;
            curState[f.fname].geometries=geometries;
            curState[f.fname].variables=variables;
            this.setState({newFiles:curState});
        }

        if (this.state.id===undefined){
            return(null);
        }
        let useableGeoms=[];        
        for (let fname in this.state.newFiles){
            let tJSX=[];            
            let fileContents=this.state.newFiles[fname];
            for (let g of this.props.data.old.geometries){
                useableGeoms.push({ind:useableGeoms.length,name:g.name,GeoID:g.GeoID,old:true});
            }
            
            if (fileContents.enabled){
                for (let i=0; i< fileContents.geometries.length;i++){
                    if (fileContents.geometries[i].enabled){
                        useableGeoms.push({ind:useableGeoms.length,name:fileContents.geometries[i].name,GeoID:'',old:false});
                    }
                    tJSX.push(<ConfigGeom 
                                    geom={fileContents.geometries[i]}
                                    index={i}
                                    key={fname+"_g"+i}
                                    fname={fname}
                                    ids={fileContents.variables}
                                    othergeometries={this.props.data.old.geometries}
                                    changeCallback={chgCall}
                                />);
                }
                // TODO Match identifier field with existing (or new) geometry
                for (let i=0; i<fileContents.variables.length;i++){
                    if ((fileContents.variables[i].type.includes('numeric')) || 
                        (fileContents.variables[i].type.includes('int')) ||
                        (fileContents.variables[i].type.includes('float'))
                        ){
                        tJSX.push(<ConfigVar 
                            key={fname+"_v"+i}
                            variable={fileContents.variables[i]}
                            index={i}
                            fname={fname}
                            ids={fileContents.variables} 
                            useableGeoms={useableGeoms}
                            othervariables={this.props.data.old.variables}
                            changeCallback={chgCall}
                        />);
                    }
                    else {
                        fileContents.variables[i].enabled=false;
                    }
                }    
            }
            retJSX.push(<div className='OneFile'>
                            <div className="OneLine" style={{display:'flex',margin:'auto',width:'fit-content'}}>
                                <input 
                                    className="checkboxes"
                                    type="checkbox"
                                    checked={this.state.newFiles[fname].enabled}
                                    data-fname={fname}                                    
                                    onChange={(e)=>{
                                        let curState={...this.state.newFiles};
                                        let newF=e.target.getAttribute('data-fname');
                                        curState[newF].enabled=!curState[newF].enabled;
                                        this.setState({newFiles:curState});
                                    }}
                                />            
                                {fname}
                            </div>
                            {tJSX} 
                        </div>);
        }
        retJSX.push(<button key="run" className="commonButton" onClick={()=>{
                            console.log(this.state);
                            let sendConfig={}
                            sendConfig.id=this.state.id;
                            sendConfig.newFiles={};
                            for (let f in this.state.newFiles) {
                                if (this.state.newFiles[f].enabled===false){
                                    continue;
                                }
                                sendConfig.newFiles[f]={}
                                sendConfig.newFiles[f].enabled=true;
                                sendConfig.newFiles[f].geometries=[];
                                for (let g of this.state.newFiles[f].geometries){
                                    if (g.enabled){
                                        sendConfig.newFiles[f].geometries.push(g);
                                    }
                                }
                                sendConfig.newFiles[f].variables=[];
                                for (let v of this.state.newFiles[f].variables){
                                    if (v.enabled){
                                        let cV={...v};
                                        if (cV.useGeom!==''){
                                            cV.useGeom=useableGeoms[parseInt(v.useGeom,10)]
                                        }
                                        sendConfig.newFiles[f].variables.push(cV);
                                    }
                                }

                            }
                            console.log(sendConfig);
                            sendData(getURL.MoveTemporary(),sendConfig,(ret)=>{
                                let msg="Problems processing "
                                let show=false;
                                for (let f in ret){
                                    if (!ret[f]){
                                        msg=msg+f+', '
                                        show=true
                                    }
                                }
                                if (show){
                                    msg=msg.slice(0,msg.length-2)+'.'
                                    alert(msg)
                                }
                                else {
                                    this.setState({id:undefined,newFiles:undefined});
                                }
                            })
                        }}>
                        OK
                    </button>);
        retJSX.push(<button 
                        key="reset" 
                        className="commonButton" 
                        onClick={()=>{
                            let curFiles={...this.state.newFiles};
                            for (let fname in curFiles){
                                for (let i=0;i<curFiles[fname].geometries.length;i++){
                                    curFiles[fname].geometries[i].enabled=true;
                                    curFiles[fname].geometries[i].indexField='';
                                    curFiles[fname].geometries[i].mergeWith='';
                                }
                                for (let i=0;i<curFiles[fname].variables.length;i++){
                                    curFiles[fname].variables[i].enabled=true;
                                    curFiles[fname].variables[i].indexField='';
                                    curFiles[fname].variables[i].mergeWith='';
                                }
                            }                    
                            this.setState({newFiles:curFiles});                                        
                        }}>
                        Reset
                    </button>)
        retJSX.push(<button 
                        key="selNone" 
                        className="commonButton" 
                        onClick={()=>{
                            let curFiles={...this.state.newFiles};
                            for (let fname in curFiles){
                                for (let i=0;i<curFiles[fname].geometries.length;i++){
                                    curFiles[fname].geometries[i].enabled=false;
                                }
                                for (let i=0;i<curFiles[fname].variables.length;i++){
                                    curFiles[fname].variables[i].enabled=false;
                                }
                            }                    
                            this.setState({newFiles:curFiles});
                        }}>
                        Select none
                    </button>)
                    return(retJSX);
    }
}

export default ConfigNewStuff;