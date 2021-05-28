import './App.css';
import React, {useEffect} from 'react';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import {useForm, Controller} from "react-hook-form";
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import {makeStyles} from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    root: {
        marginTop: '4rem',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-end',
    },
    spacing: {
        paddingTop: '0.7rem',
        width: "100%",
    },
    formControl: {
        width: '100%',
    }
}))

function App() {
    const {control, handleSubmit, reset} = useForm();
    const classes = useStyles()

    useEffect(() => {
        document.title = 'Indeed Bot'
    }, [])

    const onSubmit = (data) => {
        fetch('http://localhost:8000/run ', {
            body: JSON.stringify(data),
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: "POST",
        }).then(r => r.json()).then(() => reset())
    }

    const formControls = [
        {
            'id': 'email',
            'name': 'email',
            'label': 'Email',
            'type': 'email',
        }, {
            'id': 'password',
            'name': 'password',
            'label': 'Password',
            'type': 'password',
        },
        {
            'id': 'what',
            'name': 'what',
            'label': 'Job name',
            'type': ' text',
        },
        {
            'id': 'where',
            'name': 'where',
            'label': 'Job location',
            'type': 'text',
        },
    ]

    return (
        <Container maxWidth='sm' className={classes.root}>
            <Typography variant='h4'>
                Automatic applying for Indeed jobs.
            </Typography>

            <div className={classes.spacing}/>
            <div className={classes.spacing}/>
            <div className={classes.spacing}/>

            <form onSubmit={handleSubmit(onSubmit)} className={classes.form}>
                <Grid container spacing={2}>
                    {formControls.map((fc, i) => <Grid key={i} item xs={12}>
                        <Controller
                            name={fc.name}
                            control={control}
                            rules={{
                                required: true,
                            }}
                            render={({field: {value, ...rest}, fieldState: {error}}) =>
                                <TextField id={fc.id}
                                           label={fc.label}
                                           type={fc.type}
                                           variant="outlined"
                                           className={classes.formControl}
                                           helperText={error?.message}
                                           error={!!error}
                                           {...rest}
                                />
                            }/>

                    </Grid>)}
                </Grid>
                <div className={classes.spacing}/>
                <Button variant="contained" color="primary" type='submit'>
                    Run
                </Button>
            </form>
        </Container>
    );
}

export default App;
