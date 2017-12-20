import { toString } from 'lodash';
import { Link } from 'react-router-dom';
import React, { Component } from 'react';

import Schema from 'src/components/common/Schema';
import getPath from 'src/util/getPath';


class Label extends Component {
  render() {
    const { short = false, icon = false } = this.props;
    let { title, name, file_name, schema } = this.props.entity;
    title = toString(title);
    name = toString(name);
    file_name = toString(file_name);

    if (!short && title && file_name && title !== file_name) {
        return (
            <span className="entity-label" title={title}>
                <span className="title">{title} </span>
                <span className="file-name">{file_name}</span>
            </span>
        );
    }
    
    return (
      <span className="entity-label" title={ title || name }>
        {icon && (
          <Schema.Icon schema={schema} />
        )}
        { title || name }
      </span>
    );
  }
}

class EntityLink extends Component {
  render() {
    const { entity, className, icon, short } = this.props;
    
    return (
      <Link to={getPath(entity.links.ui)} className={className}>
        <Label entity={entity} icon={icon} short={short} />
      </Link>
    );
  }
}

class Entity {
  static Label = Label;
  static Link = EntityLink;
}

export default Entity;