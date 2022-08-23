import * as React from 'react';
import CloseIcon from '@mui/icons-material/Close';
import { Snackbar, IconButton, Checkbox, FormControlLabel } from '@mui/material';

export function StyleOption(props) {

    return (
        <FormControlLabel
          value={props.value}
          control={<Checkbox 
                        onChange={props.setValue} 
                        style={props.style}
                        className={props.className}/>}
          label={props.label}
          labelPlacement="end"
        />
    )
}

export function Notify(props) {
    const action = (
        <React.Fragment>
          <IconButton
            size="small"
            aria-label="close"
            color="inherit"
            onClick={props.handleClose}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </React.Fragment>
      );

    return (
        <Snackbar
            open={props.open}
            autoHideDuration={6000}
            onClose={props.handleClose}
            message={props.message}
            action={action}
        />
    )
}