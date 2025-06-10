/*******************************************************************************
 * Copyright (c) 2009-2013 SKRATCHDOT.COM
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * http://www.eclipse.org/legal/epl-v10.html
 *  
 * Contributors:
 *     JEFF |:at:| SKRATCHDOT |:dot:| COM
 *******************************************************************************/
package com.skratchdot.electribe.model.esx.perspective;

import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

public class Alternative implements IPerspectiveFactory {
	public static final String ID = "com.skratchdot.electribe.model.esx.perspective.Alternative"; //$NON-NLS-1$

	/**
	 * Creates the initial layout for a page.
	 */
	public void createInitialLayout(IPageLayout layout) {
		layout.setEditorAreaVisible(true);
		layout.addView("org.eclipse.ui.views.PropertySheet", IPageLayout.RIGHT,
				0.75f, IPageLayout.ID_EDITOR_AREA);
		layout.addView("com.skratchdot.electribe.fileexplorer.views.TableView",
				IPageLayout.BOTTOM, 0.7f, IPageLayout.ID_EDITOR_AREA);
	}

}
