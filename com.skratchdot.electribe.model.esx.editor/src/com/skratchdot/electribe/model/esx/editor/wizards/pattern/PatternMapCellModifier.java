/*******************************************************************************
 * Copyright (c) 2009-2013 SKRATCHDOT.COM
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * http://www.eclipse.org/legal/epl-v10.html
 *  
 * Contributors:
 *     JEFF |:at:| SKRATCHDOT |:dot:| COM
 *******************************************************************************/
package com.skratchdot.electribe.model.esx.editor.wizards.pattern;

import org.eclipse.jface.viewers.ICellModifier;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.swt.widgets.TableItem;

public class PatternMapCellModifier implements ICellModifier {
	private TableViewer viewer;

	public PatternMapCellModifier(TableViewer viewer) {
		super();
		this.viewer = viewer;
	}

	@Override
	public boolean canModify(Object element, String property) {
		return true;
	}

	@Override
	public Object getValue(Object element, String property) {
		if (property == "source") {
			return ((PatternMap) element).source;
		} else if (property == "destination") {
			return ((PatternMap) element).destination;
		}
		return null;
	}

	@Override
	public void modify(Object element, String property, Object value) {
		TableItem item = (TableItem) element;

		if (property == "source") {
			((PatternMap) item.getData()).source = ((Integer) value).intValue();
		} else if (property == "destination") {
			((PatternMap) item.getData()).destination = ((Integer) value)
					.intValue();
		}
		viewer.update(item.getData(), null);
	}

}
